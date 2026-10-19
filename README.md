# sudio — Suno Studio Power Tool

CLI + Liquid Noir web dashboard for heavy Suno users (4,624+ songs, Angelika, Blak Pearl, Cold Case, etc.).

## Web Dashboard
Upload a Suno workspace CSV export → instant stats, stem-export priority list, and persona breakdown.

## Install (CLI)
```bash
git clone https://github.com/sterl27/sudio.git
cd sudio
pip install -e .
```

## Commands
```bash
sudio analyze data/suno.csv
sudio priority data/suno.csv
sudio stats data/suno.csv
sudio suggest
```

## Vercel Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/sterl27/sudio)

Drop your exported CSVs in the `data/` folder.
