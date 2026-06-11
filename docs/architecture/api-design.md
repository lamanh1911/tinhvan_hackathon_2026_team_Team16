# API Design

Base URL: `/api/v1`

All responses: `Content-Type: application/json`
Error format: `{ "error": { "code": "...", "message": "..." } }`

## Endpoints by Feature

### FR-01: Business Card Digitization

| Method | Path | Description |
|---|---|---|
| POST | `/cards/scan` | Upload card image, trigger OCR + AI extraction |
| GET | `/cards/{id}` | Get extracted card data with confidence scores |
| PATCH | `/cards/{id}` | Update fields after user correction |
| POST | `/cards/{id}/confirm` | Confirm card and create/link customer record |

### FR-02: Thank-you Email Draft

| Method | Path | Description |
|---|---|---|
| POST | `/emails/thank-you` | Generate thank-you email draft for a customer |
| GET | `/emails/{id}` | Get email draft |
| PATCH | `/emails/{id}` | Update draft content |
| POST | `/emails/{id}/send` | Send approved email (requires status: approved) |

### FR-03: Online Schedule Proposal

| Method | Path | Description |
|---|---|---|
| POST | `/schedule/online` | Propose 3-4 conflict-free online slots |
| GET | `/schedule/{id}` | Get proposal with member availability breakdown |
| POST | `/schedule/{id}/approve` | Approve a slot and include in email |

### FR-04: Offline Schedule Proposal

| Method | Path | Description |
|---|---|---|
| POST | `/schedule/offline` | Propose slots with travel buffer |

### FR-05: MOM Summarization

| Method | Path | Description |
|---|---|---|
| POST | `/meetings/{id}/transcript` | Upload transcript or recording file |
| POST | `/meetings/{id}/mom` | Generate MOM draft from transcript |
| GET | `/meetings/{id}/mom` | Get MOM draft |
| PATCH | `/meetings/{id}/mom` | Update MOM fields |
| POST | `/meetings/{id}/mom/approve` | Approve MOM |

### FR-06: Follow-up Email Draft

| Method | Path | Description |
|---|---|---|
| POST | `/emails/follow-up` | Generate follow-up email from approved MOM |

### Health

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Returns 200 when service is ready |

## Draft Status Transitions

```
draft → in_review → approved → sent
                  ↘ rejected
```

Only `POST /emails/{id}/send` transitions to `sent`, and only when current status is `approved`.
