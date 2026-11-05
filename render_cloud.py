import json, os, subprocess, requests, time, hashlib, sys, io
from PIL import Image

with open('guion.json', 'r') as f:
    data = json.load(f)

escenas = data.get('escenas', [])
props = {"scenes": []}
os.makedirs('public', exist_ok=True)

VOZ_NARRADOR = "es-CO-GonzaloNeural"
CF_ACCOUNT = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
CF_TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN")
CF_URL = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/ai/run/@cf/black-forest-labs/flux-1-schnell"

def get_audio_duration(path):
    result = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    return float(result.stdout.strip()) if result.stdout.strip() else 3.0

def generar_imagen_cloudflare(prompt, idx, img_path):
    if not CF_ACCOUNT or not CF_TOKEN:
        raise Exception("❌ FALLO CRÍTICO: Faltan las credenciales de Cloudflare.")
        
    headers = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json", "Accept": "image/png"}
    prompt_unico = f"{prompt} (escena {idx+1}, variación {int(time.time()) % 10000})"
    payload = {"prompt": prompt_unico, "steps": 4}
    
    print(f"  ☁️ Escena {idx+1} → Generando...")
    try:
        r = requests.post(CF_URL, headers=headers, json=payload, timeout=60)
        if r.status_code == 200 and len(r.content) > 10000:
            # CONVERSIÓN FORZADA A JPG REAL CON PILLOW
            try:
                img = Image.open(io.BytesIO(r.content)).convert('RGB')
                img.save(img_path, 'JPEG', quality=92)
                print(f"     ✅ Imagen JPG real generada: {os.path.getsize(img_path)//1024}KB")
                return True
            except Exception as e:
                raise Exception(f"Pillow no pudo convertir la imagen: {e}")
        else:
            raise Exception(f"Cloudflare devolvió HTTP {r.status_code}. Texto: {r.text[:200]}")
    except Exception as e:
        print(f"     ❌ ERROR FATAL EN ESCENA {idx+1}: {e}")
        sys.exit(1)

total_video = 0.0
hashes_generados = []

print("🚀 INICIANDO RENDERIZADO ESTRICTO (JPG CONVERTIDO CON PILLOW)...")

for i, escena in enumerate(escenas):
    audio_path = f"audio_{i}.mp3"
    subprocess.run(["edge-tts", "--voice", VOZ_NARRADOR, "--text", escena["texto"], "--write-media", audio_path], check=True)
    subprocess.run(["cp", audio_path, "public/"], check=True)

    audio_dur = get_audio_duration(audio_path)
    scene_duration = audio_dur + 0.4
    total_video += scene_duration
    print(f"  🎙️ Escena {i+1}: Audio {audio_dur:.2f}s + 0.4s = {scene_duration:.2f}s")

    img_path = f"img_{i}.jpg"
    generar_imagen_cloudflare(escena["img_prompt"], i, img_path)
    
    with open(img_path, 'rb') as f:
        hashes_generados.append(hashlib.md5(f.read()).hexdigest()[:8])
    subprocess.run(["cp", img_path, "public/"], check=True)

    props["scenes"].append({"text": escena["texto"], "audio": audio_path, "image": img_path, "duration": scene_duration})

with open('props.json', 'w') as f:
    json.dump(props, f, indent=2)

print("\n📊 === DIAGNÓSTICO ESTRICTO DE IMÁGENES ===")
unicos = len(set(hashes_generados))
for i, h in enumerate(hashes_generados):
    print(f"  Escena {i+1}: Hash {h}")

if unicos != len(escenas):
    print(f"🚨 ALERTA: {unicos}/{len(escenas)} imágenes únicas.")
    sys.exit(1)
else:
    print(f"✅ ÉXITO: {unicos}/{len(escenas)} imágenes únicas.")
    print(f"✅ Duración total: {total_video:.2f}s")
