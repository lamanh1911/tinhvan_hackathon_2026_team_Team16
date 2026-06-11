# Implementation Plan

> Status: APPROVED — MVP decisions confirmed and locked 2026-06-11. Ready for implementation.
> All 5 MVP decisions are final. Sprint 1 may begin.

## MVP Decisions (confirmed 2026-06-11)

| # | Question | Decision |
|---|---|---|
| 1 | Email template source | Static file in repo — no Outlook/Graph integration for MVP |
| 2 | Card confidence threshold | Threshold = 0.7 — field flagged nếu confidence < 0.7 |
| 3 | Meeting slot duration | 60 min default, configurable later |
| 4 | Transcript source for FR-05 | Manual file upload (txt/docx) — no Teams Graph transcript in MVP |
| 5 | AI model | Gemini 3.5 Flash via OpenRouter; PII masked before request; provider no-log policy applied |

---

## Overview

| Sprint | Focus | Tasks | Priority |
|---|---|---|---|
| Sprint 1 | Foundation — infra, skeleton, DB | T-01, T-02, T-03, T-16 | Must |
| Sprint 2 | FR-01: Business Card Digitization | T-04, T-05 | Must |
| Sprint 3 | FR-02: Thank-you Email | T-06, T-07 | Must |
| Sprint 4 | FR-03: Online Schedule Proposal | T-08, T-09 | Must |
| Sprint 5 | FR-05 + FR-06: MOM + Follow-up Email | T-10, T-11, T-12, T-13 | Must |
| Sprint 6 | FR-04: Offline Schedule + Hardening | T-14, T-15, T-SEC, T-E2E, T-DEPLOY | Should + Hardening |

---

## Sprint 1 — Foundation

### T-01: FastAPI Backend Skeleton

**Goal:** Runnable FastAPI app with health endpoint, config, and CORS.

**Files to create:**

```
src/api/
  main.py                 FastAPI app factory, CORS middleware, router registration
  config.py               pydantic-settings BaseSettings (all env vars typed + validated)
  routers/
    health.py             GET /health → { "status": "ok" }
  requirements.txt        fastapi, uvicorn, pydantic-settings, sqlalchemy, alembic,
                          psycopg2-binary, python-multipart, httpx, msal
```

**Key implementation rules:**
- `config.py` must fail fast on startup if any required env var is missing
- CORS must allow Next.js origin (configurable via env var `FRONTEND_URL`)
- `GET /health` returns `200 { "status": "ok" }` — used by Railway healthcheck
- No business logic in `main.py` — only app wiring

**Definition of done:**
- `uvicorn src.api.main:app` starts without errors
- `GET /health` returns 200
- Missing env var raises `ValidationError` on startup

---

### T-02: Next.js 14 Frontend Skeleton

**Goal:** Runnable Next.js app with layout, Tailwind, icon libraries, and mock auth.

**Files to create:**

```
src/components/
  app/
    layout.tsx            Root layout: font, Tailwind base classes, AuthProvider wrapper
    page.tsx              Dashboard placeholder (redirects to /cards after auth)
    (features)/
      cards/page.tsx      Placeholder
      emails/page.tsx     Placeholder
      schedule/page.tsx   Placeholder
      meetings/page.tsx   Placeholder
  components/
    ui/
      StatusBadge.tsx     Reusable draft status badge (Draft/In Review/Approved/Sent)
      LoadingSpinner.tsx  SVG spinner, no text
      ErrorMessage.tsx    Inline error display
    layout/
      Sidebar.tsx         Navigation sidebar — SVG icons only, no emoji
      Header.tsx          Top bar with user info
  lib/
    types.ts              TypeScript types matching all Pydantic schemas
    api-client.ts         Fetch wrapper: base URL, JSON parse, error normalization
    constants.ts          DRAFT_STATUS values, ROUTES, API_BASE
  package.json
  tsconfig.json           strict: true
  tailwind.config.ts
  next.config.ts
```

**Key implementation rules:**
- Install: `@heroicons/react`, `react-icons` — no emoji anywhere
- `StatusBadge.tsx` uses color + text label only (no emoji in label)
- Mock auth: `AuthProvider` interface with `useAuth()` hook, hard-coded user for phase 1
- `api-client.ts` normalizes all errors to `{ code, message }` shape

**Definition of done:**
- `next dev` starts without TypeScript errors
- Dashboard page renders without console errors
- `StatusBadge` renders all 4 statuses correctly

---

### T-03: Database Models + Initial Alembic Migration

**Goal:** All 7 SQLAlchemy models defined, initial migration file generated and tested.

**Files to create:**

```
src/api/
  models/
    __init__.py
    base.py               DeclarativeBase, UUID PK helper, TIMESTAMPTZ columns
    customer.py           Customer model (soft delete: deleted_at)
    business_card.py      BusinessCard model (FK: customer_id, indexed)
    meeting.py            Meeting model (FK: customer_id, indexed; soft delete)
    meeting_minutes.py    MeetingMinutes model (FK: meeting_id, indexed)
    action_item.py        ActionItem model (FK: minutes_id, indexed)
    email_draft.py        EmailDraft model (FK: meeting_id, indexed; all statuses)
    member.py             Member model (role: Sales/BrSE/Admin)
  alembic/
    env.py                Alembic config pointing to models metadata
    versions/
      0001_initial_schema.py   upgrade() creates all 7 tables; downgrade() drops them
  alembic.ini
```

**Key implementation rules:**
- All PKs: `UUID`, server-default `gen_random_uuid()`
- All timestamps: `TIMESTAMPTZ`, not naive datetime
- Foreign key columns must have `index=True`
- `email_draft.status` CHECK constraint: `('draft','in_review','approved','sent','rejected')`
- `meeting.mode` CHECK constraint: `('online','offline')`
- `member.role` CHECK constraint: `('Sales','BrSE','Admin')`
- `downgrade()` must be implemented — no empty stub

**Definition of done:**
- `alembic upgrade head` applies migration without errors on a fresh PostgreSQL database
- `alembic downgrade -1` reverts cleanly
- All 7 tables exist with correct columns, types, constraints, and indexes

---

### T-16: railway.json + Health Endpoint Verification

**Goal:** Backend deployable to Railway with correct start command and health check.

**Files to create/update:**

```
railway.json              Backend service config (see deployment-architecture.md)
.env.example              All required env vars with empty values, comments explaining each
```

**railway.json content:**
- `startCommand`: `alembic upgrade head && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
- `healthcheckPath`: `/health`
- `restartPolicyType`: `ON_FAILURE`

**Definition of done:**
- `railway.json` validates against Railway JSON schema
- All env vars in `.env.example` match `config.py` field names

---

## Sprint 2 — FR-01: Business Card Digitization

### T-04: Card Scanner Service + API

**Goal:** Upload card image → OCR → LLM field extraction → confidence scores → stored draft.

**Files to create:**

```
src/api/
  services/
    storage_client.py     Upload/download from Railway S3 (boto3 or httpx)
    card_scanner.py       Google Vision OCR → raw text → OpenRouter extraction
    llm_client.py         OpenRouter gateway: JSON-mode requests, model selection, no-log policy
  routers/
    cards.py              4 endpoints: POST /cards/scan, GET /cards/{id},
                          PATCH /cards/{id}, POST /cards/{id}/confirm
  schemas/
    cards.py              CardScanRequest, CardFieldsResponse, CardConfirmRequest
                          FieldWithConfidence: { value: str, confidence: float, flagged: bool }
```

**Confidence threshold rule (MVP decision #2):**
- Confidence ≥ 0.7 → field accepted
- Confidence < 0.7 → `flagged: true` — user phải xem lại và sửa trước khi confirm
- Required fields (name, company, email) missing hoàn toàn → block confirm

**Business rules to enforce (from business-rules.md):**
- BR-01: If name, company, or email is missing or confidence < 0.7 → `flagged: true`, user must fill
- BR-02: Flagged fields appear highlighted — user must correct before confirming
- BR-03: Internal module only — no third-party card scanning SDK

**LLM prompt design:**
- System prompt: extract exactly these fields from OCR text — name, company, title, email, phone, address
- Output must be JSON with `value` and `confidence` per field
- Mask PII (email, phone) before logging — pass raw to LLM only (MVP decision #5)
- Model: Gemini 3.5 Flash via OpenRouter with provider no-log policy (NFR-SEC-05)

**Draft flow:**
- `POST /cards/scan` → stores image to S3, runs OCR + LLM, creates `business_cards` record
- `POST /cards/{id}/confirm` → creates or links `customers` record

**Definition of done:**
- Uploading a JPEG card returns structured fields with confidence scores
- Fields with confidence < 0.7 have `flagged: true`
- `POST /cards/{id}/confirm` fails if name/company/email are missing or still flagged
- PII does not appear in any log line

---

### T-05: Card Capture UI

**Goal:** Upload card, view extracted fields with confidence indicators, edit inline, confirm.

**Files to create:**

```
src/components/app/(features)/cards/
  page.tsx                Card capture page (Server Component for initial load)
  [id]/
    page.tsx              Card review page — field editor + confirm button
components/cards/
  CardUpload.tsx          Drag-and-drop + file picker, calls POST /cards/scan
  CardFieldEditor.tsx     Form with all 6 fields; flagged fields highlighted in amber
  ConfidenceIndicator.tsx Visual bar or label (no emoji) — Low / Medium / High
  CardActions.tsx         Confirm button (disabled until required fields valid)
```

**UI rules:**
- Flagged fields: amber border + "Needs review" label (text only, no emoji)
- Confidence levels: text labels "Low", "Medium", "High" + color bar
- Confirm button: disabled state if name/company/email are empty
- Loading state: SVG spinner during scan (no text emoji)
- All icons: heroicons only

**Definition of done:**
- Uploading a card shows all extracted fields with confidence indicators
- Flagged fields are visually distinct and editable
- Confirm button is disabled until all required fields are filled
- No emoji anywhere on the page

---

## Sprint 3 — FR-02: Thank-you Email Draft

### T-06: Thank-you Email Draft API

**Goal:** Read calendar event via Graph, inject into static template, generate draft via Gemini, store as draft.

**Files to create:**

```
src/api/
  services/
    graph_client.py       Microsoft Graph: get calendar events (event name, date, attendees)
    email_template.py     Load static template from repo, inject placeholders
  routers/
    emails.py             POST /emails/thank-you, GET /emails/{id},
                          PATCH /emails/{id}, POST /emails/{id}/send
  schemas/
    emails.py             ThankYouEmailRequest, EmailDraftResponse, EmailSendRequest
                          EmailStatus: Literal['draft','in_review','approved','sent','rejected']
  templates/
    thank_you_email.txt   Static company email template with placeholders:
                          {{event_name}}, {{meeting_date}}, {{customer_name}}, {{schedule_slots}}
```

**MVP decision #1 — Static template:**
- Template is a committed text file at `src/api/templates/thank_you_email.txt`
- `email_template.py` reads the file and substitutes placeholders using customer + calendar data
- No Outlook/Graph template fetch in MVP

**Microsoft Graph scopes required (app-only):**
- `Calendars.Read` — read meeting event (event name, date, attendees) only

**Business rules to enforce:**
- BR-04: Use fixed company email template — inject event name + date into template
- BR-05: Email body must include event name and exact meeting date (from calendar event)
- BR-06: If schedule proposal is requested, include slot options from FR-03
- BR-20: New draft always starts with `status: "draft"`

**`POST /emails/{id}/send` guard:**
- Must reject with `400 INVALID_STATUS` if current status is not `approved`
- Only this endpoint triggers actual email send — no other path sends email

**Definition of done:**
- Draft generated using static template with correct event name and date injected
- `POST /emails/{id}/send` with non-approved draft returns 400
- `email_drafts` row has `status: draft` immediately after generation
- No PII or email body content in logs

---

### T-07: Email Draft Review UI

**Goal:** Show editable email draft, status badge, send button (enabled only when approved).

**Files to create:**

```
src/components/app/(features)/emails/
  page.tsx                Email list (drafts + sent)
  [id]/
    page.tsx              Email detail: editor + status badge + actions
components/emails/
  EmailDraftEditor.tsx    Rich text editor (or textarea) for editing email body
  DraftStatusBadge.tsx    Extends StatusBadge — shows Draft/In Review/Approved/Sent
  EmailActions.tsx        Submit for review → Approve → Send buttons
                          Each button only enabled in correct state
  AttendeeInfo.tsx        Display which customer + event the email is for
```

**UI state machine:**

```
Draft       → [Submit for Review] button enabled
In Review   → [Approve] button enabled (BrSE/Sales role)
Approved    → [Send] button enabled (Sales role only)
Sent        → Read-only, all buttons disabled
Rejected    → [Edit] re-opens draft for revision
```

**Definition of done:**
- Send button disabled unless status is `approved`
- Status badge visible on all states
- User can edit body in Draft and Rejected states only
- No emoji in any button or label

---

## Sprint 4 — FR-03: Online Schedule Proposal

### T-08: Calendar Service + Schedule Proposal API

**Goal:** Query all attendee calendars, find 3-4 conflict-free time slots, return proposals.

**Files to create:**

```
src/api/
  services/
    graph_client.py       Add: get_free_busy(member_ids, start, end) → availability blocks
  routers/
    schedule.py           POST /schedule/online, GET /schedule/{id},
                          POST /schedule/{id}/approve
  schemas/
    schedule.py           ScheduleOnlineRequest, SlotProposal, MemberAvailability,
                          ScheduleProposalResponse
```

**Slot-finding algorithm:**
1. Call Graph `getSchedule` for all required members over a search window (default: next 10 business days)
2. Find 60-min windows where ALL members are free (MVP decision #3: default duration = 60 min, configurable via `MEETING_DURATION_MINUTES` env var)
3. Return exactly 3-4 slots (BR-07)
4. If fewer than 3 found, expand search window by 5 business days (BR-09)
5. Each slot includes per-member `free/busy` status

**Microsoft Graph scopes required:**
- `Calendars.Read` — read free/busy of all members

**Business rules to enforce:**
- BR-07: Exactly 3-4 slots proposed
- BR-08: No slot conflicts with any required attendee
- BR-09: Expand search window if fewer than 3 slots found

**Definition of done:**
- Returns 3-4 slots with no conflicts
- Each slot has per-attendee availability status
- When Graph is unavailable → 503 with `INTEGRATION_ERROR` (NFR-REL-01)

---

### T-09: Schedule Proposal UI

**Goal:** Display proposed slots with attendee availability table; let user approve a slot.

**Files to create:**

```
src/components/app/(features)/schedule/
  page.tsx                Schedule proposal trigger page
  [id]/
    page.tsx              Proposal review: slot list + attendee availability
components/schedule/
  SlotList.tsx            List of 3-4 proposed slots with date/time
  AttendeeAvailability.tsx Table: slot × attendee → Free/Busy indicator (color + text)
  SlotApproveButton.tsx   Approve button per slot; calls POST /schedule/{id}/approve
```

**UI rules:**
- Free/Busy: color-coded cells + text ("Free" / "Busy") — no emoji
- Selected slot: highlighted with border + "Selected" label
- Approve button: disabled after selection is made (prevent double-click)

**Definition of done:**
- All 3-4 slots visible with attendee availability breakdown
- Selecting and approving a slot persists via API
- No conflicts shown in approved slot

---

## Sprint 5 — FR-05 + FR-06: MOM + Follow-up Email

### T-10: MOM Summarization Service + API

**Goal:** Accept manually uploaded transcript file, generate structured MOM draft, store for review.

**Files to create:**

```
src/api/
  services/
    transcript_parser.py  Parse uploaded txt/docx file → raw text string
  routers/
    meetings.py           POST /meetings/{id}/transcript  (multipart/form-data, txt or docx),
                          POST /meetings/{id}/mom,
                          GET /meetings/{id}/mom,
                          PATCH /meetings/{id}/mom,
                          POST /meetings/{id}/mom/approve
  schemas/
    meetings.py           TranscriptUploadRequest, MOMDraftResponse, MOMApproveRequest
                          ActionItemSchema: { description, owner, deadline }
```

**MVP decision #4 — Manual file upload:**
- User uploads a `.txt` or `.docx` transcript file via `POST /meetings/{id}/transcript`
- `transcript_parser.py` extracts plain text: `.txt` read directly, `.docx` via `python-docx`
- No Teams Graph transcript integration in MVP

**MOM generation:**
- Input: raw transcript text from uploaded file
- LLM (Gemini 3.5 Flash via OpenRouter): produce JSON with `summary`, `next_actions[]` (each with `owner`, `deadline`), `language`
- Validate output: all 4 fields present, each action item has `owner` and `deadline` (BR-13, BR-14)
- If transcript incomplete → include `incomplete_warning` flag in response (BR-15)

**Transcript handling (NFR-SEC-03):**
- Transcript text is passed to LLM and then discarded — not stored in DB in raw form
- Only the generated MOM is persisted

**Definition of done:**
- User can upload `.txt` or `.docx` file and get a structured MOM draft
- MOM has all 4 required fields after generation
- Action items with missing owner or deadline are rejected with `VALIDATION_ERROR`
- Transcript content does not appear in logs
- Raw transcript not stored in `meeting_minutes` — only summary + action items

---

### T-11: MOM Review UI

**Goal:** Display 4-field MOM, editable action items, approve button.

**Files to create:**

```
src/components/app/(features)/meetings/
  page.tsx                Meeting list
  [id]/
    mom/page.tsx          MOM review page
components/meetings/
  MOMSummary.tsx          Main discussion points (textarea, editable in draft state)
  ActionItemList.tsx      List of action items with owner + deadline fields
  ActionItemRow.tsx       Single action item: description, owner, deadline — all editable
  MOMActions.tsx          Add item button + Approve MOM button
  MissingFieldWarning.tsx Warning banner if any of 4 required fields is empty (text only, no emoji)
```

**Validation in UI:**
- Approve button disabled if any action item is missing owner or deadline
- Missing required fields show inline validation message (text, no emoji)

**Definition of done:**
- All 4 MOM fields visible and editable in draft state
- Approve button blocked when validation fails
- User can add/remove action items
- No emoji in any label or button

---

### T-12: Follow-up Email Draft API

**Goal:** Generate follow-up email from approved MOM, suggest relevant attachments.

**Files to create/update:**

```
src/api/
  routers/
    emails.py             Add: POST /emails/follow-up
  schemas/
    emails.py             Add: FollowUpEmailRequest, AttachmentSuggestion
  services/
    llm_client.py         Add: generate_follow_up_email(mom, attachment_pool) → draft + suggestions
```

**Business rules to enforce:**
- BR-16: Email body summarizes meeting discussion (from MOM summary)
- BR-17: All next actions from MOM are listed in the email
- BR-18: Attachment suggestions reference topics discussed
- `POST /emails/follow-up` fails with `400 INVALID_STATUS` if MOM is not `approved`

**Definition of done:**
- Email draft references all action items from the MOM
- Attachment suggestions are returned alongside the draft
- MOM status must be `approved` before generation — otherwise 400

---

### T-13: Follow-up Email Review UI

**Goal:** Review follow-up email draft, see attachment suggestions, send after approval.

**Files to create:**

```
src/components/app/(features)/emails/
  [id]/page.tsx           Reuse from T-07 (EmailDraftEditor) — follow-up type shows attachment panel
components/emails/
  AttachmentSuggestions.tsx  Checklist of suggested attachments (checkbox + file name, no emoji)
```

**UI rules:**
- Attachment suggestions: checkboxes with file names — no emoji
- Same send-button state machine as T-07 (Draft → In Review → Approved → Send)

**Definition of done:**
- Follow-up email shows attachment suggestions panel
- Send button follows same approval flow as thank-you email

---

## Sprint 6 — FR-04: Offline Schedule + Hardening

### T-14: Offline Schedule Service

**Goal:** Extend online schedule with Google Maps travel buffer.

**Files to create/update:**

```
src/api/
  services/
    maps_client.py        Google Maps Distance Matrix API:
                          get_travel_time(origin, destination, departure_time) → minutes
  routers/
    schedule.py           Add: POST /schedule/offline
  schemas/
    schedule.py           Add: ScheduleOfflineRequest (adds location, departure fields),
                          SlotWithBuffer (adds travel_buffer_minutes)
```

**Business rules to enforce:**
- BR-10: Travel buffer from Google Maps added to slot boundaries
- BR-11: No slot placed where travel between consecutive appointments is infeasible
- BR-12: No slot adjacent to "Company visit" calendar events

**Definition of done:**
- Each proposed slot includes `travel_buffer_minutes`
- No slot created where prior appointment + travel time > slot start
- "Company visit" events block adjacent slots

---

### T-15: Offline Schedule UI

**Goal:** Extend schedule proposal UI with travel buffer display.

**Files to create/update:**

```
components/schedule/
  SlotWithBuffer.tsx      Extends SlotList — shows travel buffer time per slot (e.g., "30 min travel")
```

**Definition of done:**
- Travel buffer shown per slot in plain text (no emoji)
- Infeasible slots not shown

---

### T-SEC: Security Review Pass

**Scope:** Entire `src/` — run `security-reviewer` agent.

**Checklist:**
- No PII in any log statement (search for `logger.*name|email|phone` patterns)
- No hardcoded secrets (search for API key patterns in code)
- All `approved → sent` transitions gated behind status check
- Microsoft Graph scopes documented and not over-permissioned (NFR-SEC-02)
- OpenRouter calls for PII/transcript use no-log model (NFR-SEC-05)
- `email_drafts.status` CHECK constraint enforced at DB level

**Output:** Security findings report in `docs/context/known-issues.md`.

---

### T-E2E: End-to-End Tests

**Scope:** `tests/` — run `qa-engineer` agent with `playwright-cli` and `webapp-testing` skills.

**Test files to create:**

```
tests/
  unit/
    test_card_scanner.py      OCR extraction, confidence scoring, flagging logic
    test_email_drafter.py     Template injection, event/date validation
    test_scheduler.py         Conflict detection, slot count, window expansion
    test_mom_summarizer.py    4-field validation, action item validation
  integration/
    test_graph_client.py      Mock Graph responses — free/busy, calendar events, transcript
    test_storage_client.py    Mock S3 upload/download
  e2e/
    test_card_flow.spec.ts    Upload card → review fields → confirm → customer created
    test_email_flow.spec.ts   Generate draft → edit → approve → send
    test_schedule_flow.spec.ts  Propose slots → no conflicts → approve slot
    test_mom_flow.spec.ts     Upload transcript → generate MOM → edit → approve
```

**Key assertions per test (from acceptance criteria):**
- Draft status starts as `draft` — assert no auto-send
- Email draft contains correct event name and date
- No proposed slot conflicts with any attendee
- MOM has all 4 fields; action items have owner and deadline
- Low-confidence card fields are flagged

---

### T-DEPLOY: Final Railway Deploy

**Steps:**
1. Backend: `alembic upgrade head` runs before server start (already in `railway.json`)
2. Frontend: `next build` passes with no TypeScript errors
3. Set all environment variables in Railway Variables dashboard (not in code)
4. Verify `GET /health` returns 200 in Railway deploy logs
5. Smoke test each FR endpoint via deployed URL

**Pre-deploy checklist (`.claude/rules/06-review-checklist.md`):**
- All items in the review checklist pass
- `railway.json` present and valid
- `.env` not committed
- All required vars in `.env.example`

---

## Cross-cutting Concerns

### Mock Strategy for External APIs

During Sprint 1-2, external API credentials may not yet be available.

| Service | Mock approach |
|---|---|
| Microsoft Graph | `MockGraphClient` implementing `GraphClientProtocol` — returns fixture data |
| Google Vision | Return pre-built OCR response JSON fixture |
| Gemini 3.5 Flash (OpenRouter) | Return pre-built JSON fixture for each feature |
| Google Maps | Return fixed travel time (e.g., 30 min) from env var |

Mocks are swapped via `config.py` flag `USE_MOCKS=true`.

### Error Handling

All integration failures return a consistent error shape:

```json
{ "error": { "code": "INTEGRATION_ERROR", "message": "Microsoft Graph unavailable" } }
```

Never return a partial or guessed response when an external service fails (NFR-REL-01).

### Language Support

Email drafts and MOM generation should pass through the detected language of the card or transcript to OpenRouter. The LLM prompt should specify: "Generate the output in the same language as the input" (NFR-USA-01).

