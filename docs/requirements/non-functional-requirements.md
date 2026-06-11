# Non-Functional Requirements

## Human-in-the-Loop

| Code | Requirement |
|---|---|
| NFR-HIL-01 | AI must not send email or book meetings automatically — all output requires human review |
| NFR-HIL-02 | Every draft (email, MOM, schedule) must be editable before use |
| NFR-HIL-03 | Low-confidence extracted fields must be flagged for user review |

## Integration

| Code | Requirement |
|---|---|
| NFR-INT-01 | Business card scanning uses an internal module (OCR + AI extraction) — no third-party card scanning apps |
| NFR-INT-02 | Microsoft Outlook integration for reading templates and creating email drafts |
| NFR-INT-03 | Microsoft Teams Calendar for reading availability of multiple attendees |
| NFR-INT-04 | Teams Transcript or recording as source for MOM generation |
| NFR-INT-05 | Google Maps Platform for travel time calculation |

## Accuracy

| Code | Requirement |
|---|---|
| NFR-ACC-00 | Card scanner must correctly extract required fields (name, company, email), support multilingual cards, and provide confidence scores |
| NFR-ACC-01 | Email draft must reference the correct event name and meeting date |
| NFR-ACC-02 | No proposed schedule slot may conflict with any required attendee |
| NFR-ACC-03 | Offline slots must include correct travel buffer — slots must not be too close together |
| NFR-ACC-04 | MOM must contain all 4 required fields; each next action must have an owner and deadline |

## Performance

| Code | Target | Baseline |
|---|---|---|
| NFR-PERF-01 | Thank-you email draft generation | Below ~15 min |
| NFR-PERF-02 | Online schedule proposal | Below 5-10 min |
| NFR-PERF-03 | Offline schedule proposal | Below ~10 min |
| NFR-PERF-04 | MOM generation | Below ~5 min |

## Security and Privacy

| Code | Requirement |
|---|---|
| NFR-SEC-01 | Customer PII (name, email, phone) must not appear in application logs |
| NFR-SEC-02 | Calendar and transcript access must be scoped to required members only — no over-permissioned access |
| NFR-SEC-03 | Transcript and meeting content must be used only for MOM generation — must not be retained in raw form or forwarded |
| NFR-SEC-04 | Third-party service integrations (Google Maps) must comply with internal security policy |
| NFR-SEC-05 | PII and transcript data sent to OpenRouter must use a model or route with a no-log policy; data flow and retention must be documented |

## Usability

| Code | Requirement |
|---|---|
| NFR-USA-01 | Support language appropriate to customer context (e.g., Japanese for Japanese-language business emails) |
| NFR-USA-02 | Draft review interface must allow fast inline editing before sending |
| NFR-USA-03 | Use a fixed company email template to ensure brand consistency |

## Reliability

| Code | Requirement |
|---|---|
| NFR-REL-01 | When calendar or transcript is unavailable, show a clear error — do not generate a partial or incorrect output |
| NFR-REL-02 | When card data is incomplete, prompt the user to fill in missing fields — do not guess |
