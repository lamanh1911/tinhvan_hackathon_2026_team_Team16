# Functional Requirements

Reference: BA docs in `tinhvan_hackathon_2026_team_16/docs/`

## FR-01 - Business Card Digitization

**Priority:** Must

| | Detail |
|---|---|
| Input | Business card image (camera capture or file upload) |
| Output | Structured customer data: name, company, title, email, phone, address — with confidence score per field |
| AI does | OCR reads text, LLM extracts and normalizes fields |
| Human does | Verify name, company, email before proceeding |

**Business Rules:**
- Must extract at minimum: name, company, email
- Low-confidence fields must be visually flagged for user review
- Module is internal — no third-party card scanning apps

**Acceptance Criteria:**
- User can digitize a card using only the internal module
- Extracted fields are shown for user review before proceeding
- Fields with low confidence or missing values are marked for correction

---

## FR-02 - Thank-you Email Draft

**Priority:** Must

| | Detail |
|---|---|
| Input | Customer info (FR-01), Teams Calendar, company email template |
| Output | Draft thank-you email customized with event name and meeting date |
| AI does | Read calendar, generate draft |
| Human does | Review wording, then send |

**Business Rules:**
- Use fixed company business template
- Email must mention: event where they met, date of meeting, thank-you message
- If follow-up meeting needed, include schedule proposal (FR-03 or FR-04)

**Acceptance Criteria:**
- Draft mentions the correct event and date matching the customer
- User can edit draft before sending
- Draft status starts as "Draft"

---

## FR-03 - Online Meeting Schedule Proposal

**Priority:** Must

| | Detail |
|---|---|
| Input | Calendar availability of all required attendees (Teams Calendar) |
| Output | 3-4 conflict-free time slots |
| AI does | Read calendars, find free windows |
| Human does | Approve the preferred slot |

**Business Rules:**
- Propose exactly 3-4 slots
- Check all required attendees' calendars
- No proposed slot may conflict with any existing event

**Acceptance Criteria:**
- No proposed slot conflicts with any required attendee's calendar
- Display shows which attendees are free or busy at each slot

---

## FR-04 - Offline Meeting Schedule Proposal

**Priority:** Should

Extends FR-03 with travel time.

| | Detail |
|---|---|
| Input | Attendee calendars, meeting location address, departure location |
| Output | Slots with travel buffer included |
| AI does | Cross-reference calendars, calculate travel time via Google Maps |
| Human does | Confirm which attendees are required |

**Business Rules:**
- Add travel time buffer between appointments
- Do not propose slots adjacent to "Company visit" calendar events
- Avoid slots too close together

**Acceptance Criteria:**
- Each slot includes appropriate travel buffer
- No slot placed so close to another that travel is not feasible

---

## FR-05 - MOM Summarization

**Priority:** Must

| | Detail |
|---|---|
| Input | Teams meeting transcript or recording |
| Output | MOM with: main discussion points, next actions, owners, deadlines |
| AI does | Summarize transcript, generate structured MOM |
| Human does | Review and approve MOM content |

**Business Rules:**
- MOM must contain all 4 required fields: summary, next actions, owners, deadlines
- Each next action must have an assigned owner and deadline

**Acceptance Criteria:**
- MOM is never missing any of the 4 required fields
- Each next action has an owner and deadline
- User can add, edit, or remove action items before approving

---

## FR-06 - Follow-up Email Draft

**Priority:** Must

| | Detail |
|---|---|
| Input | Approved MOM (FR-05), company documents (profile, case study) |
| Output | Draft follow-up email with attachment suggestions |
| AI does | Generate draft from MOM content |
| Human does | Review content, then send |

**Business Rules:**
- Email must summarize the meeting
- Email must mention all agreed next actions
- Suggest relevant attachments based on meeting context

**Acceptance Criteria:**
- Draft accurately reflects next actions from the MOM
- Attachment suggestions are relevant to the discussed topics
- Draft status starts as "Draft"
