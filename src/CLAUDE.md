# src/ - Source Code

This is a monorepo with two distinct parts:

| Directory | Language | Framework | Purpose |
|---|---|---|---|
| `components/` | TypeScript | Next.js 14 App Router | Frontend UI |
| `api/` | Python | FastAPI | Backend API |
| `lib/` | TypeScript | — | Shared types and utilities |

## Rules

- Frontend (`components/`): read `.claude/rules/02-frontend-rules.md` before any UI work
- Backend (`api/`): read `.claude/rules/03-backend-rules.md` before any API work
- Database: read `.claude/rules/04-database-rules.md` before any schema change
- All code: read `.claude/rules/00-project-policy.md` for core constraints

## Key Constraint

No AI output (email draft, MOM, schedule proposal) may be sent or confirmed without explicit user action. Draft status must always be enforced in both API and UI.
