# Project Structure — AI Sales Follow-up Assistant (Relay)

Monorepo gồm **frontend (Next.js)** + **backend (FastAPI)** + tài liệu + cấu hình AI agent.

```
ai-sales-follow-up-assistant/
├── src/
│   ├── api/                 # Backend — Python FastAPI
│   ├── components/          # Frontend — Next.js 14 (App Router)
│   └── lib/                 # Kiểu/util dùng chung
├── docs/                    # Tài liệu: requirements, architecture, context, tasks
├── tests/                   # Bộ test tự động (pytest unit/integration + Playwright e2e)
├── .claude/                 # Cấu hình AI agent: rules, skills, agents, commands
├── railway.json             # Cấu hình deploy backend (Railway/Nixpacks)
├── requirements.txt         # Trỏ tới src/api/requirements.txt (để Nixpacks nhận diện Python)
├── .env.example             # Liệt kê biến môi trường cần thiết
├── CLAUDE.md / AGENTS.md    # Hướng dẫn cho AI agent + danh sách agent
└── prompt-history*.md       # Lịch sử prompt (minh chứng dự thi)
```

## Backend — `src/api/` (Python FastAPI)

```
src/api/
├── main.py                  # Khởi tạo FastAPI app, CORS, đăng ký router
├── config.py                # pydantic-settings (đọc biến môi trường)
├── database.py              # SQLAlchemy engine + session (get_db)
├── exceptions.py            # AppError + error handler (định dạng lỗi chuẩn)
├── routers/                 # Tầng API (1 file / nhóm nghiệp vụ)
│   ├── health.py            #   GET /health
│   ├── cards.py             #   FR-01 Số hóa danh thiếp
│   ├── meetings.py          #   FR-05 MOM (biên bản họp)
│   ├── emails.py            #   FR-02 Thank-you + FR-06 Follow-up
│   └── schedule.py          #   FR-03/04 Đề xuất lịch họp
├── services/                # Tầng nghiệp vụ / tích hợp ngoài
│   ├── llm_client.py        #   OpenRouter (card vision, MOM, email)
│   ├── card_scanner.py      #   Orchestrate quét card
│   ├── mom_summarizer.py    #   Sinh MOM từ transcript
│   ├── transcript_parser.py #   Parse .txt/.docx
│   ├── email_template.py    #   Template email cố định
│   ├── graph_client.py      #   Microsoft Graph (mock — calendar/free-busy)
│   └── storage_client.py    #   Object storage (S3)
├── models/                  # SQLAlchemy ORM (1 bảng / file)
│   ├── base.py, customer.py, business_card.py, meeting.py,
│   │   meeting_minutes.py, action_item.py, email_draft.py, member.py
├── schemas/                 # Pydantic request/response (theo nhóm nghiệp vụ)
│   ├── cards.py, meetings.py, emails.py, schedule.py
├── templates/               # Template email tĩnh (thank_you_email.txt)
└── alembic/                 # Migration DB (versions/0001 … 0006)
```

**Quy ước backend**
- Mỗi router = một nhóm nghiệp vụ (FR-xx). Mọi endpoint trả JSON theo Pydantic schema.
- Lỗi theo định dạng chuẩn `{ "error": { "code", "message" } }` (xem `exceptions.py`).
- Không log PII (tên/email/phone/transcript). Secrets chỉ qua biến môi trường.
- Đổi schema DB **bắt buộc** qua Alembic migration.

## Frontend — `src/components/` (Next.js 14 App Router)

```
src/components/
├── app/                     # App Router
│   ├── layout.tsx, page.tsx
│   └── (features)/          # Nhóm route theo tính năng
│       ├── cards/           #   FR-01: /cards, /cards/[id]
│       ├── meetings/        #   FR-05: /meetings, /meetings/[id]/mom
│       ├── emails/          #   FR-02/06: /emails, /emails/[id]
│       └── schedule/        #   FR-03/04: /schedule
├── components/              # Component tái sử dụng (1 component / file)
│   ├── ui/                  #   StatusBadge, LoadingSpinner, ErrorMessage…
│   ├── layout/              #   Sidebar, Header
│   ├── cards/ meetings/ emails/ schedule/   # Component theo tính năng
├── lib/                     # api-client, types, constants, auth
├── railway.json             # Cấu hình deploy frontend (npm start, health /cards)
└── package.json, tsconfig.json, tailwind.config.ts
```

**Quy ước frontend**
- TypeScript strict, không `any`. 1 component / file, tên file PascalCase trùng tên component.
- Tailwind utility, không inline style. **Không emoji**; icon dùng SVG (heroicons).
- Type API ở `lib/types.ts` khớp với Pydantic schema backend.
- Mọi draft hiển thị `StatusBadge` (Draft / In Review / Approved / Sent).

## Tài liệu — `docs/`

```
docs/
├── requirements/    PRD, functional/non-functional requirements, designs
├── architecture/    system-overview, api-design, database-design, deployment-architecture
├── context/         business-rules, domain-glossary, known-issues, tool-changelog
├── tasks/           backlog, implementation-plan
├── templates/       ADR / PRD / TASK templates
└── project-structure.md   (file này)
```

## Cấu hình AI agent — `.claude/`

```
.claude/
├── rules/      00-project-policy … 06-review-checklist (quy tắc bắt buộc khi code)
├── skills/     frontend-design, microsoft-graph, tdd … (skill hỗ trợ)
├── agents/     backend-engineer, frontend-engineer, qa-engineer …
└── commands/   slash command (/test-all, /pre-pr-review …)
```

## Quy ước đặt tên (tổng hợp)
| Đối tượng | Quy ước | Ví dụ |
|---|---|---|
| Bảng DB | snake_case, số nhiều | `email_drafts`, `action_items` |
| Cột / FK | snake_case / `{bảng}_id` | `customer_id`, `meeting_id` |
| Module Python | snake_case | `mom_summarizer.py` |
| Class Python | PascalCase | `MOMSummarizerService` |
| Component React | PascalCase (file trùng tên) | `StatusBadge.tsx` |
| Route Next.js | kebab/segment theo tính năng | `/meetings/[id]/mom` |
| Migration | `000N_<mô tả>.py` | `0005_schedule_proposals.py` |
```
