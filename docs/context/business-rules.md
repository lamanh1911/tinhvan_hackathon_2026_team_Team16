# Business Rules

Rules extracted from functional requirements. Reference these when implementing any feature.

## Card Scanning (FR-01)

- BR-01: Minimum required fields: name, company, email. If any are missing or low-confidence, the user must be prompted to fill them in before proceeding.
- BR-02: Low-confidence fields must be visually flagged — the user must be able to correct them inline before confirming.
- BR-03: The internal card scanner module handles all card digitization. No third-party card scanning apps.

## Thank-you Email (FR-02)

- BR-04: Use the company's fixed email template. Do not deviate from the template structure.
- BR-05: The email must mention the event where the customer was met and the exact date.
- BR-06: If a follow-up meeting is needed, the email should include proposed schedule slots.

## Online Schedule (FR-03)

- BR-07: Always propose exactly 3-4 time slots.
- BR-08: All required attendees' calendars must be checked. No slot may conflict with any required attendee.
- BR-09: If fewer than 3 conflict-free slots are found, expand the search window.

## Offline Schedule (FR-04)

- BR-10: Travel time between locations must be calculated via Google Maps and added as a buffer.
- BR-11: No slot may be placed so close to an adjacent appointment that travel between locations is not feasible.
- BR-12: No slot may conflict with calendar events marked "Company visit".

## MOM (FR-05)

- BR-13: MOM must always contain all 4 required fields: main discussion points, next actions, owners, deadlines.
- BR-14: Every next action must have an assigned owner and a deadline. A next action without both is invalid.
- BR-15: If the transcript is incomplete, the system should indicate which sections may be missing — do not guess.

## Follow-up Email (FR-06)

- BR-16: The email must summarize the meeting discussion.
- BR-17: The email must explicitly mention all agreed next actions from the MOM.
- BR-18: Attachment suggestions must be based on the topics discussed in the meeting.

## General

- BR-19: AI never sends email or books meetings automatically. Every send action requires explicit user confirmation.
- BR-20: All drafts start with `status: "draft"`. Status transitions are: draft → in_review → approved → sent.
- BR-21: Only the Sales role can send emails to customers. BrSE can approve but not send.
