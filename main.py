from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import pandas as pd
from pathlib import Path
import tempfile
import shutil

from sudio.parser import load_suno_library
from sudio.analyzer import analyze

app = FastAPI(title="sudio — Suno Web Dashboard")

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head><title>sudio Dashboard</title>
    <style>body{font-family: system-ui; padding: 40px; background: #0f0f0f; color: #fff;}</style>
    </head>
    <body>
    <h1>🚀 sudio — Suno Power Tool</h1>
    <p>Upload your suno.csv export</p>
    <form action="/analyze" enctype="multipart/form-data" method="post">
        <input type="file" name="file" accept=".csv">
        <button type="submit">Analyze Library</button>
    </form>
    </body>
    </html>
    """

@app.post("/analyze")
async def analyze_upload(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    df = load_suno_library(tmp_path)
    total = df["songs"].sum()
    top = df.nlargest(10, "songs")[["name", "songs"]].to_dict(orient="records")
    
    Path(tmp_path).unlink()
    
    return {
        "total_songs": int(total),
        "folders": len(df),
        "top_folders": top,
        "message": "✅ Analysis complete. Top priority folders ready for stem export."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
