# Known Issues

## Security Findings (T-SEC — 2026-06-13)

---

## [SEC-1] mark_sent endpoint bypassed approval gate

- **Discovered:** 2026-06-13
- **Severity:** High
- **Component:** backend — `src/api/routers/emails.py`
- **Description:** `POST /emails/{id}/mark-sent` was transitioning directly to `"sent"` without checking that the email was in `"approved"` state. An unapproved draft could be marked sent by calling the alias endpoint instead of the main `/send` endpoint.
- **Workaround:** N/A
- **Status:** Resolved — `_transition(email, {"approved"}, "sent")` is now enforced on both endpoints. Commit included in T-SEC pass.

---

## [SEC-2] Missing X-No-Log header on LLM calls containing PII

- **Discovered:** 2026-06-13
- **Severity:** High
- **Component:** backend — `src/api/services/llm_client.py`
- **Description:** `GeminiVisionClient` (card image upload — may contain name, phone, address) and `OpenRouterLLMClient` (transcript summarization — contains full meeting transcript with names and conversation) were missing the `"X-No-Log": "true"` header. OpenRouter logs requests by default; this would expose PII to a third-party logging system.
- **Workaround:** N/A
- **Status:** Resolved — `"X-No-Log": "true"` added to headers in both clients. Commit included in T-SEC pass.

---

## [SEC-3] Filename logged on card upload (potential PII)

- **Discovered:** 2026-06-13
- **Severity:** Medium
- **Component:** backend — `src/api/routers/cards.py`
- **Description:** The card scan endpoint logged `filename=<original_filename>` from the uploaded file. Files are frequently named after the person (e.g., `NguyenVanA.jpg`, `Alice_BusinessCard.png`), which would expose PII in application logs.
- **Workaround:** N/A
- **Status:** Resolved — log statement changed to log only `content_type`. Commit included in T-SEC pass.

---

## Deploy Readiness Report (T-DEPLOY — 2026-06-13)

### Frontend Build

| Check | Result |
|---|---|
| `npx tsc --noEmit` | PASS — 0 errors |
| `npx next build` | PASS — 10 routes compiled, 0 warnings |
| No emoji in UI | PASS (rule enforced in `.claude/rules/02-frontend-rules.md`) |
| All icons are SVG | PASS |

### Backend Environment Variables

Required vars (no default — must be set in Railway):

| Variable | Present in `.env.example` | Notes |
|---|---|---|
| `DATABASE_URL` | Yes | Railway PostgreSQL connection string |
| `SECRET_KEY` | Yes | App signing key |

Optional vars with defaults (safe to deploy without, mocks used):

| Variable | Default | Notes |
|---|---|---|
| `USE_MOCKS` | `false` | Set `true` for dev without external API keys |
| `OPENROUTER_API_KEY` | `""` | Required for real LLM (MOM, email draft) |
| `OPENROUTER_MODEL` | `google/gemini-2.5-flash` | Documented in `.env.example` |
| `AZURE_TENANT_ID / CLIENT_ID / SECRET` | `""` | Required for real MS Graph (calendar, transcript) |
| `GOOGLE_VISION_API_KEY` | `""` | Required for real card OCR |
| `GOOGLE_MAPS_API_KEY` | `""` | Required for real travel time (offline schedule) |
| `STORAGE_ACCESS_KEY / SECRET_KEY / BUCKET / ENDPOINT` | `""` | Required for real S3 storage |

### Railway Config

| Check | Result |
|---|---|
| `railway.json` present | PASS |
| `healthcheckPath` set | — (verify in Railway dashboard) |
| Start command includes Alembic migration | Verify `startCommand` in Railway dashboard |
| `.env` not committed | PASS (in `.gitignore`) |

### Recommended Start Command (Railway)

```
alembic -c src/api/alembic.ini upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
```

### Open Items Before Production Deploy

1. Set `SECRET_KEY` and `DATABASE_URL` in Railway Variables dashboard.
2. Set `USE_MOCKS=false` and configure real API keys for all integrations.
3. Confirm `healthcheckPath` is set to `/health` in Railway dashboard.
4. Run `alembic upgrade head` against the Railway PostgreSQL instance and verify all 6 migrations apply cleanly.
5. Rotate any keys that were accidentally committed to `.env` during development.

---

## Test Coverage Summary (T-E2E — 2026-06-13)

| Suite | Files | Tests | Status |
|---|---|---|---|
| Unit | 4 files | 78 tests | 78/78 PASS |
| Integration | 2 files | 13 tests | 13/13 PASS |
| E2E (Playwright) | 4 files | 17 tests | SKIPPED — Playwright not installed |

To enable E2E tests:
```
cd src/components
npm install -D @playwright/test
npx playwright install
```
Then remove `test.skip(true, ...)` from each `tests/e2e/*.spec.ts` file.
