# 03 - Backend Rules

## API Conventions

- Use noun-based REST paths: `/customers`, `/emails`, `/meetings`, `/schedule`
- Correct HTTP verbs: GET for read, POST for create, PATCH for partial update, DELETE for remove
- All endpoints return JSON
- Pagination uses `limit` and `offset` query parameters

## Error Response Format

All errors must follow this structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": {}
  }
}
```

Common codes: `VALIDATION_ERROR`, `NOT_FOUND`, `UNAUTHORIZED`, `INTEGRATION_ERROR`, `INTERNAL_ERROR`

## Pydantic Schemas

- Every request body must have a Pydantic input schema
- Every response must have a Pydantic output schema
- Schemas live in `src/api/schemas/`
- Never return raw SQLAlchemy model objects from endpoints

## PII Handling

- Never log: customer name, email, phone number, transcript content
- Allowed in logs: IDs, timestamps, status codes, error codes
- When calling OpenRouter with PII or transcript content, choose a model or route with a no-log policy

## Secrets

- All credentials are loaded from environment variables
- Never hardcode API keys, tokens, or passwords
- Use `pydantic-settings` (`BaseSettings`) to manage config — fail fast on missing required vars at startup

## Human-in-the-Loop Enforcement

- No endpoint may send email directly — endpoints only create or update draft records
- No endpoint may confirm a meeting booking automatically
- Draft status flow: `draft` → `in_review` → `approved` → `sent`
- Only the `approved` → `sent` transition triggers actual sending, and only when explicitly called by the user

## Integration Error Handling

- When Microsoft Graph is unavailable: return `503` with `INTEGRATION_ERROR` code, do not generate a partial response
- When OCR or LLM fails: return the error, do not guess or hallucinate output
- Never silently fall back to empty or placeholder data
