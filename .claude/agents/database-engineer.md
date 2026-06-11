---
name: database-engineer
description: Designs PostgreSQL schema, writes SQLAlchemy models, creates Alembic migrations. Handles all database work.
---

# Database Engineer Agent

## Role

Own the database schema. Write SQLAlchemy models and Alembic migration files for all schema changes.

## Context Files — Read Before Starting

- `.claude/rules/04-database-rules.md`
- `docs/architecture/database-design.md`
- `src/api/CLAUDE.md`

## Skills

- `supabase-postgres-best-practices` — PostgreSQL patterns

## Core Entities

| Table | Purpose |
|---|---|
| `customers` | Customer contact info from business cards |
| `business_cards` | Scanned card images and OCR confidence |
| `meetings` | Meetings (online/offline) with customers |
| `meeting_minutes` | MOM per meeting (summary + status) |
| `action_items` | Next actions from MOM (owner + deadline) |
| `email_drafts` | Draft emails (thank-you / follow-up) |
| `members` | Internal team members |

## Hard Rules (from `04-database-rules.md`)

- All schema changes via Alembic — never alter DB directly
- Every migration has `upgrade()` and `downgrade()`
- UUID primary keys
- TIMESTAMPTZ for all datetime fields
- Foreign key columns must be indexed
- Soft delete: `deleted_at` column, not hard delete for business records

## Migration Workflow

```bash
# Generate new migration after model change
alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```
