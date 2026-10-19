from rich.console import Console
from rich.table import Table
from .config import PERSONAS, PRIORITY_KEYWORDS

console = Console()

def analyze(df):
    total = df["songs"].sum()
    console.print(f"[bold green]Total Songs:[/] {total:,} across {len(df)} folders")
    
    # Priority score
    df = df.copy()
    lower_name = df["name"].str.lower()
    df["priority"] = df["songs"] * 0.5
    df["priority"] += lower_name.str.contains("|".join(PRIORITY_KEYWORDS)) * 150
    df["priority"] += lower_name.str.contains("stems|raw|pro") * 100
    df["priority"] += df["time_ago"].astype(str).str.contains("h ago|d ago") * 80
    
    console.print("\n[bold cyan]TOP PRIORITY FOR STEM EXPORT[/]")
    table = Table(show_header=True)
    table.add_column("Rank")
    table.add_column("Folder")
    table.add_column("Songs", justify="right")
    table.add_column("Age")
    table.add_column("Score", justify="right")
    
    for i, row in df.nlargest(20, "priority").iterrows():
        table.add_row(str(i+1), row["name"][:50], str(row["songs"]), row.get("time_ago", ""), f"{row['priority']:.0f}")
    console.print(table)
    
    console.print("\n[bold magenta]Persona Breakdown[/]")
    for p, keys in PERSONAS.items():
        mask = lower_name.str.contains("|".join(keys))
        count = df[mask]["songs"].sum()
        if count > 0:
            console.print(f"• [bold]{p}[/]: {count:,} songs")
