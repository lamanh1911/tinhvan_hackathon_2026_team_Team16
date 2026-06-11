# 00 - Project Policy

## Core Principle: Human-in-the-Loop

AI generates drafts. Humans decide before anything is sent, published, or booked.

- AI must never send email automatically
- AI must never book or confirm a meeting without human approval
- AI must never perform any action that affects external parties without user confirmation
- Every AI output must be stored as `status: "Draft"` until the user explicitly approves

This principle is non-negotiable and overrides all other considerations.

## Scope

This project implements exactly these features:

| Feature | Priority |
|---|---|
| FR-01: Business card digitization | Must |
| FR-02: Thank-you email draft | Must |
| FR-03: Online meeting schedule proposal | Must |
| FR-04: Offline meeting schedule with travel buffer | Should |
| FR-05: MOM summarization | Must |
| FR-06: Follow-up email draft | Must |

Do not add features outside this list without a requirements change.

## Data Privacy

- PII (customer name, email, phone) must never appear in application logs
- Meeting transcripts are used only as input for MOM generation — they must not be persisted in raw form beyond processing
- Secrets and tokens are stored in Railway environment variables only — never in source code or committed files

## Roles

| Role | Can Send Email | Can Approve Drafts |
|---|---|---|
| Sales | Yes | Yes |
| BrSE | No | Yes |
| Admin | No | No |
