# PRD - AI Sales Follow-up Assistant

## Purpose

AI Sales Follow-up Assistant automates the repetitive post-networking and post-meeting workflow for sales teams. The system digitizes business cards, reads calendar context, generates email drafts, proposes meeting schedules, summarizes meeting minutes, and suggests attachments.

All AI output is a draft. Humans review and decide before anything is sent.

## Problem

After every networking event or customer meeting, sales must manually:

| Pain Point | Impact |
|---|---|
| Check calendar to recall where and when they met a customer | Time lost, wrong context in emails |
| Cross-reference calendars of multiple attendees | Scheduling conflicts, repeated back-and-forth |
| Calculate travel time for in-person meetings | Appointments too close together, late arrivals |
| Review meeting transcript to fill in missed information | Incomplete or inaccurate MOM |
| Write thank-you and follow-up emails from templates | Repetitive work, inconsistent quality |

## Goals

| Goal | Metric | Baseline |
|---|---|---|
| Reduce time to thank-you email draft | Time from card scan to draft ready | ~15 min |
| Reduce time to online schedule proposal | Time to find and propose 3-4 slots | 5-10 min |
| Reduce time to offline schedule proposal | Time including travel buffer calculation | ~10 min |
| Reduce time to MOM | Time from meeting end to draft MOM | ~5 min |
| Eliminate schedule conflicts | Proposed slots conflict with any required attendee | Frequent |
| Ensure MOM completeness | MOM contains all 4 required fields | Not standardized |

## Features

| Feature | Priority | Description |
|---|---|---|
| FR-01 | Must | Business card digitization via internal OCR + AI module |
| FR-02 | Must | Thank-you email draft generation |
| FR-03 | Must | Online meeting schedule proposal (3-4 conflict-free slots) |
| FR-04 | Should | Offline meeting schedule with travel time buffer |
| FR-05 | Must | MOM summarization from Teams transcript or recording |
| FR-06 | Must | Follow-up email draft generation from MOM |

## Out of Scope

- Sending email automatically without human review
- Managing contracts or full CRM pipeline
- Booking meetings directly on behalf of the customer without confirmation

## Users

| Role | Description |
|---|---|
| Sales | Primary user — owns customer relationships, triggers workflows, sends emails |
| BrSE | Bridge engineer — supports technical content, reviews and approves MOM |
| Admin | System admin — manages config, templates, permissions |

## Non-negotiable Constraints

- Human-in-the-loop: AI never sends email or books meetings automatically
- PII (name, email, phone) must not appear in logs
- All secrets via Railway environment variables — never in code
