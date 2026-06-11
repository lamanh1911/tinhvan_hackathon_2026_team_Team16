# System Overview

## Architecture

```
[Next.js 14 Frontend]  ←→  [Python FastAPI Backend]  ←→  [PostgreSQL]
        ↕                           ↕
  [Browser client]         [External Services]
                           ├── Microsoft Graph (Outlook, Calendar, Transcript)
                           ├── Google Cloud Vision (OCR)
                           ├── Google Speech-to-Text
                           ├── Google Maps Platform
                           ├── OpenRouter (LLM gateway)
                           └── Railway Object Storage (S3)
```

## Services on Railway

| Service | Framework | Port | Health Path |
|---|---|---|---|
| frontend | Next.js 14 | 3000 | `/` |
| backend | Python FastAPI | 8000 | `/health` |
| db | Railway PostgreSQL | 5432 | managed |

## Request Flow

1. User action in browser (Next.js)
2. Next.js calls FastAPI backend via REST
3. FastAPI executes business logic:
   - Calls external APIs (Graph, Google, OpenRouter) as needed
   - Reads/writes PostgreSQL via SQLAlchemy
   - Stores/retrieves files from Railway object storage
4. FastAPI returns structured response (Pydantic schema)
5. Next.js renders updated UI

## Human-in-the-Loop Points

| Trigger | AI Action | Human Gate |
|---|---|---|
| Card image uploaded | OCR + field extraction | User verifies fields before saving |
| Card saved | Generate thank-you email draft | User reviews and clicks Send |
| Schedule requested | Propose 3-4 slots | User selects and approves slot |
| Meeting ended | Summarize transcript → MOM | User reviews and approves MOM |
| MOM approved | Generate follow-up email draft | User reviews and clicks Send |

## Authentication

- **App login (phase 1):** Mock auth for fast development. Designed as pluggable `AuthProvider` interface for future OIDC SSO with Microsoft Entra ID or Google.
- **Microsoft Graph:** App-only (client credentials flow) — backend authenticates with app registration on Entra ID. Independent of user login. Scoped via Application Access Policy.
