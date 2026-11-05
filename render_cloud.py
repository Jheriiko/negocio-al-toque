import json, os, subprocess, requests, time, hashlib, sys, io, base64
from PIL import Image

with open('guion.json', 'r') as f:
    data = json.load(f)

escenas = data.get('escenas', [])
props = {"scenes": []}
os.makedirs('public', exist_ok=True)
os.makedirs('cache', exist_ok=True)

VOZ_NARRADOR = "es-CO-GonzaloNeural"
CF_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/black-forest-labs/flux-1-schnell"

PROMPT_FALLBACK = "Colombian comic book style, 2d animation, abstract city skyline, blue and grey tones, vertical 9:16, minimalist"

def get_audio_duration(path):
    result = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    return float(result.stdout.strip()) if result.stdout.strip() else 3.0

def llamar_cloudflare(prompt, idx):
    if not CF_ACCOUNT or not CF_TOKEN:
        raise Exception("❌ Faltan credenciales de Cloudflare.")
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "steps": 4}
    r = requests.post(CF_URL, headers=headers, json=payload, timeout=60)
    if r.status_code != 200:
        raise Exception(f"HTTP {r.status_code}: {r.text[:300]}")
    if 'application/json' in r.headers.get('Content-Type', ''):
        json_data = r.json()
        if not json_data.get("success") or "image" not in json_data.get("result", {}):
            raise Exception(f"JSON sin imagen válida: {str(json_data)[:300]}")
        return base64.b64decode(json_data["result"]["image"])
    return r.content

def generar_imagen_cloudflare(prompt, idx, img_path, cache_path):
    if os.path.exists(cache_path) and os.path.getsize(cache_path) > 10000:
        print(f"  💾 Escena {idx+1} → Caché encontrada.")
        subprocess.run(["cp", cache_path, img_path], check=True)
        return True

    prompt_unico = f"{prompt} (escena {idx+1})"
    print(f"  ☁️ Escena {idx+1} → Generando...")
    try:
        img_bytes = llamar_cloudflare(prompt_unico, idx)
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        img.save(img_path, 'JPEG', quality=92)
        subprocess.run(["cp", img_path, cache_path], check=True)
        print(f"     ✅ Imagen JPG: {os.path.getsize(img_path)//1024}KB")
        return True
    except Exception as e:
        # SISTEMA DE REINTENTO CON PROMPT DE RESPALDO
        if "NSFW" in str(e) or "400" in str(e):
            print(f"     ⚠️ Prompt rechazado por NSFW. Reintentando con prompt de respaldo...")
            try:
                img_bytes = llamar_cloudflare(f"{PROMPT_FALLBACK} (escena {idx+1})", idx)
                img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
                img.save(img_path, 'JPEG', quality=92)
                subprocess.run(["cp", img_path, cache_path], check=True)
                print(f"     ✅ Imagen de respaldo generada: {os.path.getsize(img_path)//1024}KB")
                return True
            except Exception as e2:
                print(f"     ❌ Fallback también falló: {e2}")
                sys.exit(1)
        else:
            print(f"     ❌ ERROR FATAL EN ESCENA {idx+1}: {e}")
            sys.exit(1)

total_video = 0.0
hashes = []

for i, escena in enumerate(escenas):
    audio_name = f"audio_{i}.mp3"
    audio_path = f"public/{audio_name}"
    subprocess.run(["edge-tts", "--voice", VOZ_NARRADOR, "--text", escena["texto"], "--write-media", audio_path], check=True)

    audio_dur = get_audio_duration(audio_path)
    scene_duration = audio_dur + 0.4
    total_video += scene_duration

    img_name = f"img_{i}.jpg"
    img_path = f"public/{img_name}"
    cache_path = f"cache/{img_name}"
    generar_imagen_cloudflare(escena["img_prompt"], i, img_path, cache_path)

    with open(img_path, 'rb') as f:
        hashes.append(hashlib.md5(f.read()).hexdigest()[:8])

    props["scenes"].append({
        "text": escena["texto"],
        "audio": audio_name,
        "image": img_name,
        "duration": scene_duration
    })

with open('props.json', 'w') as f:
    json.dump(props, f, indent=2)

print(f"\n📊 Imágenes únicas: {len(set(hashes))}/{len(hashes)}")
print(f"✅ Duración total: {total_video:.2f}s")
if len(set(hashes)) != len(hashes):
    sys.exit(1)
