# /backend-check

Audit all backend files against `03-backend-rules.md`.

## Checks

1. **Schemas** — every router endpoint has a typed Pydantic input and output schema
2. **Error format** — all `HTTPException` and error responses use `{ "error": { "code", "message" } }`
3. **PII in logs** — scan for `logger` or `print` calls containing customer fields (name, email, phone)
4. **Hardcoded secrets** — scan for API keys, tokens, passwords in source files
5. **Draft enforcement** — no endpoint directly triggers email send or calendar booking without `status: approved` check
6. **Env vars** — all external credentials loaded via `pydantic-settings`, not `os.environ.get` with defaults

## Output

List each violation with file path and line reference. No violation = pass.
