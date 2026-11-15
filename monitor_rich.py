import subprocess
from rich.console import Console
from rich.panel import Panel
console = Console()
def monitor():
    console.print(Panel.fit("[bold cyan]Monitoreando GitHub Actions...[/bold cyan]"))
    try:
        result = subprocess.run(["gh", "run", "list", "--repo", "jheriiko/negocio-al-toque", "--limit", "3"], capture_output=True, text=True, check=True)
        console.print(result.stdout)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
if __name__ == "__main__":
    monitor()
