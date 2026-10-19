import pandas as pd
from pathlib import Path

def load_suno_library(file_path: str | Path) -> pd.DataFrame:
    """Robust loader for Suno workspace CSVs"""
    df = pd.read_csv(file_path, header=0, on_bad_lines='skip')
    
    # Fix common header issues
    if len(df.columns) < 3:
        df = pd.read_csv(file_path, header=None, on_bad_lines='skip')
        df.columns = ["image", "name", "info"] + [f"col{i}" for i in range(3, len(df.columns))]
    
    df = df.dropna(subset=["name"]).copy()
    df = df[df["name"].astype(str).str.strip() != ""]
    
    # Parse song count and age
    if "info" in df.columns:
        df[["songs", "time_ago"]] = df["info"].str.extract(r"(\d+)\s*Songs?\s*·\s*(.*)")
        df["songs"] = pd.to_numeric(df["songs"], errors="coerce").fillna(0).astype(int)
    else:
        df["songs"] = 0
        df["time_ago"] = ""
    
    return df.sort_values("songs", ascending=False).reset_index(drop=True)
