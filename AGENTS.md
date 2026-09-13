# AGENTS.md

Spotify listening analytics: a local web dashboard (FastAPI + React) plus a legacy ETL CLI that feeds a Power BI dashboard. All data comes from the Spotify Web API via Spotipy.

## Top-level layout

- `src/` — standalone ETL pipeline (CLI): extracts to `data/raw/*.csv`, transforms into `data/processed/*_clean.csv`, copies a sample to `data/sample/`, renders `data/visualizations/*.png`. Run with `python src/main.py`.
- `backend/` — FastAPI server (`backend/main.py`) that proxies the Spotify API per-session (cookie-based OAuth) for the frontend.
- `frontend/` — React 19 + Vite app (Vanilla JS, not TS). Dev server on port 5173.
- `powerbi/` — `.pbix` dashboard that reads the processed CSVs.
- `data/raw` and `data/processed` are gitignored (regenerated); `data/sample/` is committed.

## Commands

Must be run from the repo root unless noted.

```bash
# ETL CLI (needs Spotify credentials in .env)
python src/main.py

# Web app backend (port 8000)
pip install -r requirements.txt
uvicorn backend.main:app

# Frontend (port 5173)
cd frontend && npm install && npm run dev

# Frontend lint (oxlint)
cd frontend && npm run lint
```

No tests and no Python lint/typecheck config exist; CI is absent. The frontend's only lint is `oxlint`.

## Gotchas

- **`src/main.py` uses flat imports** (`from spotify_client import ...`), so it relies on its script dir being on `sys.path`. Run it as `python src/main.py` (not `python -m src.main`).
- **Two OAuth apps share one `.env`.** `src/config.py` and `backend/spotify_auth.py` both read `SPOTIFY_REDIRECT_URI` from `.env` (dev default `http://127.0.0.1:8000/callback`). Valid redirect URIs must be registered in the Spotify Developer app dashboard. `src/spotify_client.py` prints setup text telling you to use port `8888` — that guidance only refers to the redirect URI you register for the CLI; a single `.env` value serves whichever process reads it, so pick the port per task.
- **Frontend–backend coupling is hardcoded.** `frontend/src/App.jsx` calls `http://127.0.0.1:8000` (`API_URL`); backend CORS allows only `localhost:5173`; the OAuth callback redirects to `http://127.0.0.1:5173/`. Change these together.
- **Backend sessions and artwork caches are in-memory dicts** (`spotify_sessions`, `artwork_cache` in `backend/main.py`). Restarting uvicorn logs everyone out; fine for local dev only.
- No React state library — App.jsx uses plain `useState`/`useEffect`.

## Notes

- Backend scopes: `user-read-private user-top-read user-read-recently-played playlist-read-private`. CLI scopes also include `playlist-read-collaborative` — a scope difference that matters if one app works and the other doesn't.
- My personal data is generated/reset by running the CLI; do not hand-commit new CSVs into `data/` (raw/processed are ignored anyway).