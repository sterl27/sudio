import typer
from pathlib import Path
from rich import print as rprint
from .parser import load_suno_library
from .analyzer import analyze

app = typer.Typer(help="sudio — Suno Power CLI for massive libraries")

@app.command()
def analyze(
    file: Path = typer.Argument(..., exists=True, help="suno.csv or suno*.csv"),
):
    """Full analysis + priority report"""
    df = load_suno_library(file)
    analyze(df)

@app.command()
def priority(
    file: Path = typer.Argument(..., exists=True),
    limit: int = 20,
):
    """Show top folders for stem export"""
    df = load_suno_library(file)
    lower = df["name"].str.lower()
    df["score"] = df["songs"] * 0.5 + lower.str.contains("pro|lab|stems|raw|2026") * 200
    for _, row in df.nlargest(limit, "score").iterrows():
        rprint(f"[bold]{row['name']}[/] — {row['songs']} songs • {row.get('time_ago', '')}")

@app.command()
def stats(file: Path = typer.Argument(..., exists=True)):
    """Basic stats"""
    df = load_suno_library(file)
    rprint(f"[green]Folders:[/] {len(df)}")
    rprint(f"[green]Total Songs:[/] {df['songs'].sum():,}")
    rprint(f"[green]Biggest:[/] {df.iloc[0]['name']} ({df.iloc[0]['songs']} songs)")

@app.command()
def suggest():
    """Workflow recommendations"""
    rprint("[bold cyan]Recommended Workflow:[/]")
    rprint("1. sudio priority data/suno.csv")
    rprint("2. Export multitrack WAV 48kHz 24-bit from top folders in Suno Studio")
    rprint("3. Clean with Kits AI / LALAL.AI")
    rprint("4. Name: [Persona]_[Folder]_[Date]_STEM_Vocals.wav")

if __name__ == "__main__":
    app()
