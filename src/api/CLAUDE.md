# src/api/ - Python FastAPI Backend

## Stack

- Python FastAPI
- Pydantic v2 (schemas and settings)
- SQLAlchemy 2.x (ORM)
- Alembic (migrations)
- PostgreSQL (Railway managed)

## Rules (from `03-backend-rules.md`)

- Pydantic schema required for every endpoint (input and output)
- Error format: `{ "error": { "code": "...", "message": "..." } }`
- No PII in logs
- No hardcoded secrets — use `pydantic-settings`
- Drafts start as `status: "draft"` — no auto-send logic

## Directory Structure (to be created)

```
api/
  main.py               FastAPI app + CORS + router registration
  config.py             pydantic-settings BaseSettings
  routers/
    cards.py            FR-01
    emails.py           FR-02, FR-06
    schedule.py         FR-03, FR-04
    meetings.py         FR-05
    health.py           GET /health
  services/
    card_scanner.py     Google Vision + OpenRouter
    graph_client.py     Microsoft Graph (Outlook, Calendar, Transcript)
    llm_client.py       OpenRouter gateway
    maps_client.py      Google Maps Distance Matrix
    storage_client.py   Railway S3 object storage
  models/               SQLAlchemy ORM models
  schemas/              Pydantic request/response schemas
  alembic/              Alembic migration files
  requirements.txt
```

## Draft Status Flow

```
draft → in_review → approved → sent
                  ↘ rejected
```

The `sent` transition only happens when the user explicitly calls the send endpoint and status is `approved`.
