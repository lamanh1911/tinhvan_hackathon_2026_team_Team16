# Database Design

## ERD Summary

```
CUSTOMER ||--o{ BUSINESS_CARD : "digitized-from"
CUSTOMER ||--o{ MEETING      : "attends"
MEETING  ||--|| MEETING_MINUTES : "produces"
MEETING_MINUTES ||--o{ ACTION_ITEM : "contains"
MEETING  ||--o{ EMAIL_DRAFT  : "triggers"
MEMBER   ||--o{ MEETING      : "participates-in"
```

## Tables

### customers

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| name | TEXT | Yes | |
| company | TEXT | Yes | |
| title | TEXT | No | |
| email | TEXT | Yes | |
| phone | TEXT | No | |
| address | TEXT | No | |
| created_at | TIMESTAMPTZ | Yes | |
| deleted_at | TIMESTAMPTZ | No | Soft delete |

### business_cards

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| customer_id | UUID | Yes | FK → customers, indexed |
| image_ref | TEXT | Yes | S3 key |
| confidence | FLOAT | Yes | Overall extraction confidence |
| language | TEXT | No | Detected language |
| created_at | TIMESTAMPTZ | Yes | |

### meetings

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| customer_id | UUID | Yes | FK → customers, indexed |
| mode | TEXT | Yes | `online` or `offline` |
| start_time | TIMESTAMPTZ | Yes | |
| location | TEXT | No | For offline meetings |
| created_at | TIMESTAMPTZ | Yes | |
| deleted_at | TIMESTAMPTZ | No | Soft delete |

### meeting_minutes

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| meeting_id | UUID | Yes | FK → meetings, indexed |
| summary | TEXT | Yes | Main discussion points |
| status | TEXT | Yes | `draft`, `in_review`, `approved` |
| created_at | TIMESTAMPTZ | Yes | |
| updated_at | TIMESTAMPTZ | Yes | |

### action_items

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| minutes_id | UUID | Yes | FK → meeting_minutes, indexed |
| description | TEXT | Yes | |
| owner | TEXT | Yes | |
| deadline | DATE | Yes | |
| created_at | TIMESTAMPTZ | Yes | |

### email_drafts

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| meeting_id | UUID | No | FK → meetings, indexed |
| type | TEXT | Yes | `thank-you` or `follow-up` |
| status | TEXT | Yes | `draft`, `in_review`, `approved`, `sent`, `rejected` |
| body | TEXT | Yes | |
| created_at | TIMESTAMPTZ | Yes | |
| updated_at | TIMESTAMPTZ | Yes | |

### members

| Column | Type | Required | Notes |
|---|---|---|---|
| id | UUID | Yes | PK |
| name | TEXT | Yes | |
| role | TEXT | Yes | `Sales`, `BrSE`, `Admin` |
| created_at | TIMESTAMPTZ | Yes | |

## Migration Strategy

- All schema changes via Alembic: `alembic revision --autogenerate -m "description"`
- Migrations committed to `src/api/alembic/versions/`
- Start command on Railway: `alembic upgrade head && uvicorn ...`
