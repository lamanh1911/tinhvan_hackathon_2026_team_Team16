# CLAUDE.md - AI Sales Follow-up Assistant

## Project Overview

AI Sales Follow-up Assistant automates post-networking and post-meeting workflows for sales teams: business card digitization, calendar reading, thank-you email drafting, meeting schedule proposals, MOM summarization, and follow-up email generation.

Core principle: **Human-in-the-loop**. All AI-generated content is a draft. Humans review and decide before anything is sent or published.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 App Router, TypeScript, Tailwind CSS |
| Backend | Python FastAPI, Pydantic, SQLAlchemy |
| Database | PostgreSQL on Railway |
| Storage | Railway S3-compatible object storage |
| AI/OCR | Google Cloud Vision, Google Speech-to-Text, OpenRouter (LLM gateway) |
| Integrations | Microsoft Graph (Outlook, Teams Calendar, Teams Transcript), Google Maps Platform |
| Deploy | Railway (project: add85240-91e8-47ef-b390-c1fc2d14e166) |

## Rules

All rules are in `.claude/rules/`. Read them before any task:

- `00-project-policy.md` - Core principles, human-in-the-loop, scope
- `01-no-auto-implementation.md` - Plan first, approve, then implement
- `02-frontend-rules.md` - No emoji, SVG icons only, TypeScript strict
- `03-backend-rules.md` - FastAPI conventions, PII handling, error format
- `04-database-rules.md` - Alembic migrations, indexing, schema changes
- `05-railway-rules.md` - Deploy conventions, secrets management
- `06-review-checklist.md` - Pre-PR checklist

## Agents

See `AGENTS.md` for the full list of agents and their responsibilities.

## Directory Structure

```
src/
  components/   Next.js frontend (App Router, components, pages)
  api/          Python FastAPI backend
  lib/          Shared types and utilities

docs/
  requirements/     PRD, functional and non-functional requirements
  architecture/     System design, DB schema, API design, deployment
  tasks/            Backlog and implementation plan
  context/          Domain glossary, business rules, known issues
  templates/        TASK, PRD, ADR templates
```

## Key Constraints

- AI must never send email or book meetings automatically
- All drafts must remain editable before user action
- PII (name, email, phone) must never appear in logs
- Secrets live in Railway environment variables only — never in code
- Frontend: no emoji anywhere; icons must be SVG (heroicons or react-icons)
