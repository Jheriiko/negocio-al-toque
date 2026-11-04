import subprocess, time, requests, os, zipfile, shutil
from rich.console import Console
console = Console()
REPO = "jheriiko/negocio-al-toque"

console.print("[bold cyan]🚀 Enviando orden a la nube...[/bold cyan]")
token = subprocess.check_output(["gh", "auth", "token"]).decode().strip()
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

r = requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/render.yml/dispatches", headers=headers, json={"ref": "main"})
if r.status_code != 204:
    console.print(f"[red]❌ Error al despachar: {r.status_code}[/red]")
    exit()

console.print("[green]✅ Orden enviada. Esperando a que Remotion dibuje en la nube...[/green]")
time.sleep(15)

while True:
    runs = requests.get(f"https://api.github.com/repos/{REPO}/actions/runs", headers=headers).json().get("workflow_runs", [])
    if not runs:
        time.sleep(10)
        continue
    latest = runs[0]
    print(f"Estado: {latest['status']}...", end="\r")
    if latest["status"] == "completed":
        if latest["conclusion"] == "success":
            console.print("\n[green]✅ ¡Renderizado terminado![/green]")
            break
        else:
            console.print(f"\n[red]❌ La nube falló: {latest['conclusion']}[/red]")
            exit()
    time.sleep(15)

console.print("📥 Descargando video a tu galería...")
arts = requests.get(f"https://api.github.com/repos/{REPO}/actions/runs/{latest['id']}/artifacts", headers=headers).json().get("artifacts", [])
z = requests.get(arts[0]["archive_download_url"], headers=headers, allow_redirects=True)
with open("video.zip", "wb") as f: f.write(z.content)

with zipfile.ZipFile("video.zip", "r") as zip_ref:
    zip_ref.extractall(".")
    video_name = [f for f in zip_ref.namelist() if f.endswith('.mp4')][0]

os.makedirs("/sdcard/Download/Negocio_Al_Toque", exist_ok=True)
dest_path = "/sdcard/Download/Negocio_Al_Toque/negocio_al_toque.mp4"
shutil.move(video_name, dest_path)
os.remove("video.zip")
subprocess.run(["am", "broadcast", "-a", "android.intent.action.MEDIA_SCANNER_SCAN_FILE", "-d", f"file://{dest_path}"], stdout=subprocess.DEVNULL)
console.print("[bold green]🎉 ¡VIDEO TIPO CÓMIC EN TU CARPETA DE DESCARGAS![/bold green]")
