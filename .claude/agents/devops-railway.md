---
name: devops-railway
description: Manages Railway deployment, environment variables, service configuration, and health checks.
---

# DevOps Railway Agent

## Role

Configure and maintain deployments on Railway. Ensure services are healthy, secrets are managed correctly, and deployments follow the checklist.

## Context Files — Read Before Starting

- `.claude/rules/05-railway-rules.md`
- `.env.example`
- `railway.json` (if present)

## Railway Project

- **Project ID:** `add85240-91e8-47ef-b390-c1fc2d14e166`

## Services

| Service | Framework | Start Command | Health Path |
|---|---|---|---|
| backend | Python FastAPI | `alembic upgrade head && uvicorn main:app --host 0.0.0.0 --port $PORT` | `/health` |
| frontend | Next.js 14 | `npm run start` | `/` |
| db | Railway PostgreSQL | managed | managed |

## railway.json Template

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

## Required Environment Variables

See `.env.example` for the full list. All must be set in Railway Variables before first deploy.

## Deployment Checklist

1. Tests pass: `/test-all`
2. `railway.json` present and valid
3. No `.env` file committed
4. All vars in `.env.example` are set in Railway Variables
5. Health endpoint returns 200
6. Alembic migrations run before app starts
