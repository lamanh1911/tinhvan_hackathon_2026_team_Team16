# 05 - Railway Rules

## Project

- **Project ID:** `add85240-91e8-47ef-b390-c1fc2d14e166`
- All deployments target this project

## Secrets Management

- All environment variables are set via Railway Variables dashboard — never committed to the repo
- `.env.example` documents required variables with empty values — this file is safe to commit
- `.env` is in `.gitignore` and must never be committed
- Rotate secrets immediately if accidentally committed

## Service Configuration

Every service deployed to Railway must have:

- A `startCommand` defined in `railway.json` or the Railway dashboard
- A `healthcheckPath` that returns HTTP 200 when the service is ready
- A `restartPolicy` set to `on-failure`

## railway.json

Maintain a `railway.json` at project root. Minimum required structure:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "",
    "healthcheckPath": "/health",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

## Deployment Checklist

Before deploying:

1. All tests pass locally (`/test-all`)
2. `railway.json` is present and valid
3. No hardcoded secrets in any committed file
4. `DATABASE_URL` and all required env vars are set in Railway Variables
5. Health endpoint responds correctly

## Database

- Use Railway's managed PostgreSQL service
- Run Alembic migrations before starting the app: set `startCommand` to run migrations then start the server
- Never connect to the production database from a local machine during active development
