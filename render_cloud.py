import json, os, subprocess, requests, time, io, urllib.parse, sys
from PIL import Image
from rich.console import Console

console = Console()
VOZ_NARRADOR = "es-CO-GonzaloNeural"
POLL_URL = "https://image.pollinations.ai/prompt"

with open('guion.json', 'r') as f:
    data = json.load(f)

escenas = data.get('escenas', [])
os.makedirs('clips', exist_ok=True)

def get_audio_duration(path):
    r = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1", path], capture_output=True, text=True)
    return float(r.stdout.strip()) if r.stdout.strip() else 3.0

def generar_imagen_pollinations(prompt, idx):
    encoded = urllib.parse.quote(prompt)
    url = f"{POLL_URL}/{encoded}?width=1080&height=1920&model=flux&nologo=true&seed={int(time.time())%10000}"
    console.print(f"  🎨 Escena {idx+1} → Descargando imagen...")
    for _ in range(3):
        try:
            r = requests.get(url, timeout=90)
            if r.status_code == 200 and len(r.content) > 5000:
                img = Image.open(io.BytesIO(r.content)).convert('RGB')
                ipath = f"clips/img_{idx}.jpg"
                img.save(ipath, 'JPEG', quality=95)
                return ipath
        except Exception: pass
        time.sleep(5)
    raise Exception(f"Pollinations falló en escena {idx+1}")

def crear_clip_con_ffmpeg(img_path, audio_path, texto, idx, duracion):
    ass_path = f"clips/subs_{idx}.ass"
    # Limpieza básica de texto para ASS
    texto_limpio = texto.replace('\n', ' ').replace('\\', '').replace('{', '').replace('}', '').replace(',', '')
    
    ass_content = f"""[Script Info]
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,65,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,5,0,2,20,20,200,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:{duracion:05.2f},Default,,0,0,0,,{texto_limpio}
"""
    with open(ass_path, 'w') as f: f.write(ass_content)
    
    clip_path = f"clips/clip_{idx}.mp4"
    # Zoom cinematográfico + Viñeta + ASS (Texto)
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", img_path, "-i", audio_path,
        "-vf", f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0015,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(duracion*30)}:s=1080x1920:fps=30,vignette=PI/4,ass={ass_path}",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-t", str(duracion), "-pix_fmt", "yuv420p", clip_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return clip_path

total_video = 0.0
clip_paths = []

console.print("🚀 INICIANDO PIPELINE FFMPEG PURO (POLLINATIONS + ZOOM + TEXTO)...")

for i, escena in enumerate(escenas):
    audio_name = f"audio_{i}.mp3"
    audio_path = f"clips/{audio_name}"
    subprocess.run(["edge-tts", "--voice", VOZ_NARRADOR, "--text", escena["texto"], "--write-media", audio_path], check=True)
    
    dur = get_audio_duration(audio_path) + 0.4
    total_video += dur

    img_path = generar_imagen_pollinations(escena["img_prompt"], i)
    clip_path = crear_clip_con_ffmpeg(img_path, audio_path, escena["texto"], i, dur)
    clip_paths.append(clip_path)

# Unir todos los clips
console.print("🔗 Uniendo todos los clips...")
with open("concat_list.txt", "w") as f:
    for cp in clip_paths:
        f.write(f"file '{os.path.abspath(cp)}'\n")

subprocess.run([
    "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "concat_list.txt",
    "-c", "copy", "video_final.mp4"
], check=True)

console.print(f"✅ VIDEO FINAL GENERADO: video_final.mp4 ({total_video:.2f}s)")
