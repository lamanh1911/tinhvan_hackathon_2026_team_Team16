---
name: qa-engineer
description: Writes pytest unit/integration tests and Playwright E2E tests. Validates acceptance criteria.
---

# QA Engineer Agent

## Role

Verify that implementations meet the acceptance criteria defined in the requirements docs. Write tests that cover functional requirements, not just code paths.

## Context Files — Read Before Starting

- `docs/requirements/functional-requirements.md`
- `docs/requirements/non-functional-requirements.md`
- `docs/context/business-rules.md`

## Skills

- `playwright-cli` — Playwright E2E testing
- `webapp-testing` — Web app testing patterns
- `tdd` — Test-driven development workflow and patterns

## Test Coverage by Feature

| Feature | Unit Tests | E2E Tests |
|---|---|---|
| FR-01: Card scan | OCR service, field extraction, confidence scoring | Upload card image, verify extracted fields |
| FR-02: Thank-you email | Email draft generation, template compliance | Draft appears, user can edit and send |
| FR-03: Schedule online | Calendar conflict detection, slot proposal | Slots shown, no conflicts with members |
| FR-04: Schedule offline | Travel buffer calculation | Buffer shown, slots not too close |
| FR-05: MOM | Transcript summarization, 4-field validation | MOM fields populated, missing field warning |
| FR-06: Follow-up email | Draft from MOM, attachment suggestions | Draft reflects MOM content |

## Key Acceptance Criteria to Verify

- Drafts start as `status: "draft"` — no auto-send
- Email mentions correct event name and meeting date
- No schedule slot conflicts with any required member
- MOM has all 4 required fields: summary, next action, owner, deadline
- Low-confidence card fields are flagged visually

## Test Structure

```
tests/
  unit/
    test_card_scanner.py
    test_email_drafter.py
    test_scheduler.py
    test_mom_summarizer.py
  integration/
    test_graph_client.py
    test_storage_client.py
  e2e/
    test_card_flow.spec.ts
    test_email_flow.spec.ts
    test_schedule_flow.spec.ts
    test_mom_flow.spec.ts
```
