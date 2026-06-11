# 04 - Database Rules

## Schema Changes

- All schema changes must be done through Alembic migration files
- Never alter the database directly (no manual `ALTER TABLE`, `DROP COLUMN` in production)
- Every migration must have both `upgrade()` and `downgrade()` functions
- Migration files are committed to the repo

## Naming

- Table names: lowercase snake_case, plural (`customers`, `email_drafts`, `action_items`)
- Column names: lowercase snake_case
- Foreign key columns: `{referenced_table_singular}_id` (e.g., `customer_id`, `meeting_id`)
- Index names: `ix_{table}_{column}`

## Indexing

- Foreign key columns must have an index
- Columns used in frequent WHERE filters must have an index
- Add indexes in the migration file, not manually

## Data Types

- Use `UUID` for primary keys (not auto-increment integers)
- Use `TIMESTAMPTZ` for all datetime fields
- Use `TEXT` for variable-length strings without a known max (email body, transcript, summary)
- Use `VARCHAR(n)` only when there is a known business constraint on length

## Soft Deletes

- Do not hard-delete customer or meeting records
- Add `deleted_at TIMESTAMPTZ` column and filter in queries
- Hard delete is only allowed for non-business data (e.g., temporary upload records)

## Entity Reference

Core entities from the data model:

| Table | Key Fields |
|---|---|
| `customers` | id, name, company, email, phone, address |
| `business_cards` | id, customer_id, image_ref, confidence, language |
| `meetings` | id, customer_id, mode (online/offline), start_time, location |
| `meeting_minutes` | id, meeting_id, summary, status |
| `action_items` | id, minutes_id, description, owner, deadline |
| `email_drafts` | id, meeting_id, type (thank-you/follow-up), status, body |
| `members` | id, name, role |
