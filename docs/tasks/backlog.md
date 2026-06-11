# Backlog

## Priority: Must (MVP)

| ID | Feature | Depends On | Status |
|---|---|---|---|
| T-01 | Project setup: FastAPI skeleton + health endpoint | — | Pending |
| T-02 | Project setup: Next.js 14 skeleton + layout | — | Pending |
| T-03 | Database: models + Alembic initial migration | T-01 | Pending |
| T-04 | FR-01: Card scanner service (Vision + OpenRouter) | T-01, T-03 | Pending |
| T-05 | FR-01: Card capture UI (upload, preview, field editor) | T-02 | Pending |
| T-06 | FR-02: Thank-you email draft API | T-03, T-04 | Pending |
| T-07 | FR-02: Email draft review UI | T-02, T-06 | Pending |
| T-08 | FR-03: Calendar reader + slot proposer (Graph) | T-01 | Pending |
| T-09 | FR-03: Schedule proposal UI | T-02, T-08 | Pending |
| T-10 | FR-05: MOM summarizer (Transcript + OpenRouter) | T-01, T-03 | Pending |
| T-11 | FR-05: MOM review UI | T-02, T-10 | Pending |
| T-12 | FR-06: Follow-up email draft API | T-10 | Pending |
| T-13 | FR-06: Follow-up email review UI | T-02, T-12 | Pending |

## Priority: Should

| ID | Feature | Depends On | Status |
|---|---|---|---|
| T-14 | FR-04: Offline schedule with travel buffer (Google Maps) | T-08 | Pending |
| T-15 | FR-04: Offline schedule UI with travel info | T-09, T-14 | Pending |

## Infrastructure

| ID | Task | Status |
|---|---|---|
| T-16 | railway.json + health endpoint | T-01 | Pending |
| T-17 | Environment variables setup on Railway | T-16 | Pending |
| T-18 | First Railway deploy (backend) | T-16, T-17 | Pending |
| T-19 | First Railway deploy (frontend) | T-02, T-17 | Pending |
