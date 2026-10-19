from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
import tempfile
import shutil

from sudio.parser import load_suno_library
from sudio.config import PERSONAS, PRIORITY_KEYWORDS

app = FastAPI(title="sudio")

HTML = r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>sudio — Suno Power Tool</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Space+Grotesk:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #05070c;
    --cyan: #00ffc8;
    --orange: #ff6b00;
    --purple: #7b2fff;
    --glass: rgba(12, 16, 28, 0.72);
    --border: rgba(0, 255, 200, 0.18);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    min-height: 100vh;
    background: radial-gradient(1200px 600px at 80% -10%, rgba(123, 47, 255, 0.18), transparent),
                radial-gradient(900px 500px at -10% 110%, rgba(0, 255, 200, 0.08), transparent),
                var(--bg);
    color: #e8eef8;
    font-family: "Space Grotesk", system-ui, sans-serif;
  }
  header {
    padding: 28px 40px 8px;
    display: flex;
    align-items: baseline;
    gap: 16px;
  }
  h1 {
    font-family: "Bebas Neue", sans-serif;
    font-size: 52px;
    letter-spacing: 0.04em;
    margin: 0;
    color: var(--cyan);
  }
  .sub { color: #8b97ad; font-size: 15px; }
  main { padding: 12px 40px 48px; max-width: 1280px; }
  .panel {
    background: var(--glass);
    border: 1px solid var(--border);
    border-radius: 16px;
    backdrop-filter: blur(16px);
    padding: 24px;
    margin-bottom: 20px;
  }
  .drop {
    border: 1.5px dashed rgba(0, 255, 200, 0.4);
    border-radius: 14px;
    padding: 48px 24px;
    text-align: center;
    cursor: pointer;
    transition: 0.2s;
  }
  .drop:hover, .drop.drag { border-color: var(--cyan); background: rgba(0, 255, 200, 0.05); }
  input[type=file] { display: none; }
  button {
    background: var(--cyan);
    color: #05070c;
    border: 0;
    padding: 12px 22px;
    border-radius: 10px;
    font-weight: 600;
    font-family: inherit;
    cursor: pointer;
  }
  button:disabled { opacity: 0.5; cursor: wait; }
  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 14px;
    margin-bottom: 20px;
  }
  .stat {
    background: rgba(0, 255, 200, 0.06);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
  }
  .stat b { display: block; font-family: "JetBrains Mono", monospace; font-size: 28px; color: var(--cyan); }
  .stat span { color: #8b97ad; font-size: 13px; }
  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }
  th, td { padding: 10px 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.06); }
  th { color: #8b97ad; font-weight: 500; font-size: 12px; letter-spacing: 0.06em; text-transform: uppercase; }
  td.num { font-family: "JetBrains Mono", monospace; text-align: right; }
  .persona {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .persona b { color: var(--cyan); }
  #results { display: none; }
  .err { color: #ff6b6b; }
</style>
</head>
<body>
<header>
  <h1>SUDIO</h1>
  <div class="sub">Suno library analyzer · stem priority · personas</div>
</header>
<main>
  <div class="panel">
    <div class="drop" id="drop">
      <p style="margin:0 0 8px; font-size:18px;">Drop suno.csv here</p>
      <p style="margin:0 0 16px; color:#8b97ad;">or click to browse</p>
      <button type="button" id="browse">Choose file</button>
      <input type="file" id="file" accept=".csv">
    </div>
  </div>
  <div id="results">
    <div class="stats" id="stats"></div>
    <div class="panel">
      <h2 style="margin:0 0 14px; font-size:18px;">Top Priority for Stem Export</h2>
      <table id="priority"><thead><tr><th>#</th><th>Folder</th><th>Songs</th><th>Age</th><th>Score</th></tr></thead><tbody></tbody></table>
    </div>
    <div class="panel">
      <h2 style="margin:0 0 14px; font-size:18px;">Persona Breakdown</h2>
      <div id="personas"></div>
    </div>
  </div>
</main>
<script>
const drop = document.getElementById('drop');
const fileInput = document.getElementById('file');
const browse = document.getElementById('browse');
const results = document.getElementById('results');

browse.onclick = () => fileInput.click();
drop.onclick = (e) => { if (e.target === browse) return; fileInput.click(); };
drop.ondragover = (e) => { e.preventDefault(); drop.classList.add('drag'); };
drop.ondragleave = () => drop.classList.remove('drag');
drop.ondrop = (e) => {
  e.preventDefault();
  drop.classList.remove('drag');
  if (e.dataTransfer.files[0]) upload(e.dataTransfer.files[0]);
};
fileInput.onchange = () => { if (fileInput.files[0]) upload(fileInput.files[0]); };

async function upload(file) {
  results.style.display = 'none';
  const fd = new FormData();
  fd.append('file', file);
  try {
    const r = await fetch('/analyze', { method: 'POST', body: fd });
    if (!r.ok) throw new Error(await r.text());
    const data = await r.json();
    render(data);
  } catch (err) {
    alert('Failed: ' + err.message);
  }
}

function render(data) {
  document.getElementById('stats').innerHTML = `
    <div class="stat"><b>${data.total_songs.toLocaleString()}</b><span>Total songs</span></div>
    <div class="stat"><b>${data.folders}</b><span>Folders</span></div>
    <div class="stat"><b>${data.top_priority?.length || 0}</b><span>Priority targets</span></div>
  `;
  const tbody = document.querySelector('#priority tbody');
  tbody.innerHTML = (data.top_priority || []).map((row, i) => `
    <tr>
      <td>${i+1}</td>
      <td>${row.name}</td>
      <td class="num">${row.songs}</td>
      <td>${row.time_ago || ''}</td>
      <td class="num">${Math.round(row.score)}</td>
    </tr>
  `).join('');
  document.getElementById('personas').innerHTML = (data.personas || [])
    .map(p => `<div class="persona"><span>${p.name}</span><b>${p.songs.toLocaleString()}</b></div>`)
    .join('') || '<div class="sub">No persona matches</div>';
  results.style.display = 'block';
}
</script>
</body>
</html>
'''

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML

@app.post("/analyze")
async def analyze_upload(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        df = load_suno_library(tmp_path)
        total = int(df["songs"].sum())
        folders = len(df)

        lower = df["name"].str.lower()
        df = df.copy()
        df["score"] = df["songs"] * 0.5
        df["score"] += lower.str.contains("|".join(PRIORITY_KEYWORDS), regex=True) * 150
        df["score"] += lower.str.contains("stems|raw|pro", regex=True) * 100
        df["score"] += df["time_ago"].astype(str).str.contains("h ago|d ago", regex=True) * 80

        top = df.nlargest(20, "score")[["name", "songs", "time_ago", "score"]].to_dict(orient="records")

        personas = []
        for name, keys in PERSONAS.items():
            mask = lower.str.contains("|".join(keys), regex=True)
            count = int(df[mask]["songs"].sum())
            if count > 0:
                personas.append({"name": name, "songs": count})

        return {
            "total_songs": total,
            "folders": folders,
            "top_priority": top,
            "personas": personas,
        }
    finally:
        Path(tmp_path).unlink(missing_ok=True)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
