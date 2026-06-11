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
