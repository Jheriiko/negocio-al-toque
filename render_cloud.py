import json, os, subprocess, requests, urllib.parse

with open('guion.json', 'r') as f:
    data = json.load(f)

escenas = data.get('escenas', [])
props = {"scenes": []}
os.makedirs('public', exist_ok=True)

VOZ_NARRADOR = "es-CO-GonzaloNeural"
prompts_comic = [
    "colombian comic book style, 2d animation, two latin male friends talking on a street bench, vibrant colors, barrio background, vertical 9:16",
    "colombian comic book style, 2d animation, close up of hands drawing numbers on a napkin, gold peso signs, vertical 9:16",
    "colombian comic book style, 2d animation, latin man looking shocked, holding a calculator, comic expression, vertical 9:16",
    "colombian comic book style, 2d animation, two friends happily selling at a colorful street stall, vibrant, vertical 9:16",
    "colombian comic book style, 2d animation, funny comic dog with glasses working on a laptop, vertical 9:16",
    "colombian comic book style, 2d animation, two friends high-fiving, money in hands, successful, vertical 9:16"
]

for i, escena in enumerate(escenas):
    audio_path = f"audio_{i}.mp3"
    subprocess.run(["edge-tts", "--voice", VOZ_NARRADOR, "--text", escena["texto"], "--write-media", audio_path], check=True)
    subprocess.run(["cp", audio_path, "public/"], check=True)
    
    img_path = f"img_{i}.jpg"
    prompt = prompts_comic[i % len(prompts_comic)]
    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt)}?width=1080&height=1920&nologo=true&seed={i+42}&model=flux"
    print(f"Descargando imagen {i+1}...")
    r = requests.get(url, timeout=90)
    with open(img_path, 'wb') as f: f.write(r.content)
    subprocess.run(["cp", img_path, "public/"], check=True)
    
    props["scenes"].append({
        "text": escena["texto"],
        "audio": audio_path,
        "image": img_path,
        "duration": max(3.0, len(escena["texto"]) / 15 + 1.5)
    })

with open('props.json', 'w') as f:
    json.dump(props, f, indent=2)
