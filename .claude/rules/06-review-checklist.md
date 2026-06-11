# 06 - Review Checklist

Run this checklist before creating any pull request. Use `/pre-pr-review` to run it automatically.

## Human-in-the-Loop

- [ ] No endpoint sends email or books meetings automatically
- [ ] All AI-generated content is stored with `status: "draft"` initially
- [ ] Send and Approve actions require explicit user interaction
- [ ] Draft status transitions are enforced in the API

## Frontend

- [ ] No emoji in any UI element (buttons, labels, headings, toasts, placeholders)
- [ ] All icons are SVG from heroicons or react-icons
- [ ] Icon-only buttons have `aria-label`
- [ ] No TypeScript `any` types
- [ ] No inline styles
- [ ] Draft status badge is visible on all draft views

## Backend

- [ ] All endpoints have Pydantic input and output schemas
- [ ] Error responses follow the standard format `{ "error": { "code", "message" } }`
- [ ] No PII appears in log statements
- [ ] No hardcoded secrets or API keys

## Database

- [ ] Schema changes have an Alembic migration file
- [ ] Migration has both `upgrade()` and `downgrade()`
- [ ] New foreign key columns have an index

## Security

- [ ] No secrets committed (check `.env`, config files, test fixtures)
- [ ] Microsoft Graph calls use app-only auth (client credentials), not delegated user tokens
- [ ] PII and transcript data do not appear in error responses or logs

## Railway

- [ ] `railway.json` is present and `healthcheckPath` is set
- [ ] `.env` is not committed
- [ ] All required env vars are documented in `.env.example`
