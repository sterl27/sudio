# sudio — Suno Studio Power Tool

CLI + Web dashboard for heavy Suno users (4,624+ songs, Angelika, Blak Pearl, Cold Case, etc.).

## Install (CLI)
```bash
git clone https://github.com/sterl27/sudio.git
cd sudio
pip install -e .
```

## Commands
```bash
sudio analyze data/suno.csv          # Full report
sudio priority data/suno.csv         # Stem export priority list
sudio stats data/suno.csv            # Quick stats
sudio suggest                       # Workflow tips
```

## Vercel Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/sterl27/sudio)

Drop your exported CSVs in the `data/` folder.
