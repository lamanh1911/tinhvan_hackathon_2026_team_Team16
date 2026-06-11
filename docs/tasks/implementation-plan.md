# Implementation Plan

## Order of Implementation

### Sprint 1 - Foundation

1. **T-01** FastAPI skeleton: `main.py`, `health` endpoint, `pydantic-settings` config, CORS
2. **T-02** Next.js 14 skeleton: App Router layout, Tailwind CSS, `@heroicons/react`
3. **T-03** Database models + initial Alembic migration (all 6 tables)
4. **T-16** `railway.json` + deploy test to Railway

### Sprint 2 - Card Scan (FR-01)

5. **T-04** Card scanner: Google Vision OCR → OpenRouter field extraction → confidence scores
6. **T-05** Card capture UI: image upload, field preview, confidence indicators, inline edit, confirm button

### Sprint 3 - Email Draft (FR-02)

7. **T-06** Email draft API: read Teams Calendar via Graph → generate draft via OpenRouter
8. **T-07** Email draft review UI: editable draft, event/date highlight, status badge, send button

### Sprint 4 - Schedule (FR-03)

9. **T-08** Calendar service: Graph free/busy → find 3-4 conflict-free slots
10. **T-09** Schedule UI: slot list, member availability table, approve button

### Sprint 5 - MOM + Follow-up (FR-05, FR-06)

11. **T-10** MOM service: Teams Transcript → OpenRouter summarization → 4-field structured output
12. **T-11** MOM review UI: 4-field form, action items editor, approve button
13. **T-12** Follow-up email API: generate from approved MOM + attachment suggestions
14. **T-13** Follow-up email UI: draft editor, attachment checklist, send button

### Sprint 6 - Offline Schedule (FR-04) + Hardening

15. **T-14** Offline scheduler: Google Maps travel time + conflict detection
16. **T-15** Offline schedule UI: slots with travel buffer display
17. Security review pass (security-reviewer agent)
18. E2E tests (qa-engineer agent)
19. Final Railway deploy

## Notes

- Each sprint ends with `/pre-pr-review` before merging
- Mock the Microsoft Graph layer in Sprint 1-2 if tenant credentials are not yet available
- OpenRouter model selection: use a model with no-log policy for any request containing PII or transcript content
