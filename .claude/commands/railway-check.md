# /railway-check

Validate Railway deployment configuration.

## Checks

1. **railway.json** — file exists at project root, `healthcheckPath` is set, `startCommand` includes `alembic upgrade head`
2. **Health endpoint** — `GET /health` returns 200 in local dev
3. **Environment variables** — every variable in `.env.example` has a non-empty value in the current environment
4. **No committed secrets** — `.env` is not tracked by git, no API keys in any committed file
5. **Start command** — runs migrations before starting the server

## Output

List each check as PASS or FAIL with details. All must pass before deploying to Railway.
