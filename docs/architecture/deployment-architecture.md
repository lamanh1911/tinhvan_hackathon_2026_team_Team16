# Deployment Architecture

## Railway Project

**Project ID:** `add85240-91e8-47ef-b390-c1fc2d14e166`

## Services

```
Railway Project
├── frontend   (Next.js 14)
│   └── Port: auto-assigned by Railway
│   └── Health: /
│   └── Build: NIXPACKS
│
├── backend    (Python FastAPI)
│   └── Port: $PORT (Railway-assigned)
│   └── Health: /health
│   └── Start: alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
│   └── Build: NIXPACKS
│
└── db         (Railway managed PostgreSQL)
    └── Connection: DATABASE_URL env var (injected automatically)
```

## Environment Variables

Set via Railway Variables dashboard. See `.env.example` for required keys:

- `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` — Microsoft Graph
- `GOOGLE_VISION_API_KEY`, `GOOGLE_MAPS_API_KEY`, `GOOGLE_STT_API_KEY` — Google APIs
- `OPENROUTER_API_KEY` — LLM gateway
- `DATABASE_URL` — injected by Railway PostgreSQL service
- `STORAGE_ACCESS_KEY`, `STORAGE_SECRET_KEY`, `STORAGE_BUCKET`, `STORAGE_ENDPOINT` — object storage
- `SECRET_KEY` — app session/JWT secret

## railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

## Data Flow Summary

```
User browser
  → Next.js (Railway frontend)
    → FastAPI (Railway backend)
      → PostgreSQL (Railway db)
      → Railway Object Storage (card images, recordings)
      → Microsoft Graph (Outlook, Calendar, Transcript)
      → Google Cloud Vision (OCR)
      → Google Speech-to-Text (audio transcription)
      → Google Maps (travel time)
      → OpenRouter (LLM: email drafts, MOM, field extraction)
```

## Deployment — Railway native CI/CD

Monorepo deployed as **two Railway services from one GitHub repo**, plus managed Postgres.

### Monorepo build notes
- **backend** — Root Directory = `/` (repo root).
  - A root `requirements.txt` (`-r src/api/requirements.txt`) makes Nixpacks detect Python and install backend deps.
  - Root `railway.json`: start command runs Alembic migrations then uvicorn; healthcheck `/health`.
- **frontend** — Root Directory = `src/components`.
  - `src/components/railway.json`: `npm run start`, healthcheck `/`. Nixpacks runs `npm install` + `npm run build` automatically.
  - `NEXT_PUBLIC_API_BASE_URL` is inlined at **build time** — set it on the frontend service (to the backend's public URL) before the build.

### One-time setup (Railway dashboard)
1. **New → Database → PostgreSQL** (provides `DATABASE_URL`).
2. **New → GitHub Repo** → select the repo → enables auto-deploy on push (this is the CI/CD link).
3. Create two services from the repo: backend (Root `/`) and frontend (Root `src/components`).
4. Set the deploy branch (e.g. `main`) per service.
5. Backend → **Generate Domain**; copy its URL into the frontend's `NEXT_PUBLIC_API_BASE_URL`.

### Required variables per service
- **backend:** `SECRET_KEY`, `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `USE_MOCKS`, `DATABASE_URL` (reference the Postgres service). Optional real integrations: `AZURE_*`, `GOOGLE_*`, `STORAGE_*`.
- **frontend:** `NEXT_PUBLIC_API_BASE_URL` (backend public URL).

### CI/CD flow
Push to the deploy branch → Railway rebuilds and redeploys the affected service automatically. No GitHub Actions required.
