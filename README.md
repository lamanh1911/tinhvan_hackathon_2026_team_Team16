# AI Sales Follow-up Assistant

Automates post-networking and post-meeting workflows for sales teams.

## Features

| Feature | Description |
|---|---|
| FR-01 | Business card digitization (OCR + AI extraction) |
| FR-02 | Thank-you email draft generation |
| FR-03 | Online meeting schedule proposal |
| FR-04 | Offline meeting schedule with travel buffer |
| FR-05 | Meeting minutes (MOM) summarization |
| FR-06 | Follow-up email draft generation |

All AI outputs are drafts. Humans review before anything is sent.

## Demo

- **Video demo:** [Video Demo](https://tinhvan-my.sharepoint.com/:v:/p/trangnth2/IQAh3VMQC70eQ4aHvddTXFfLAaIOP71i6bnQhKsgtSK6mUU?e=bXI9vc)
- **Live app:** https://valiant-harmony-production-36ad.up.railway.app

## Stack

- **Frontend:** Next.js 14 App Router, TypeScript, Tailwind CSS
- **Backend:** Python FastAPI
- **Database:** PostgreSQL on Railway
- **Deploy:** Railway

## Getting Started

Copy `.env.example` to `.env` and fill in the required values.

```bash
# Frontend
cd src/components
npm install
npm run dev

# Backend
cd src/api
pip install -r requirements.txt
uvicorn main:app --reload
```

## Docs

- [Project Structure](docs/project-structure.md)
- [Requirements](docs/requirements/PRD.md)
- [Architecture](docs/architecture/system-overview.md)
- [Backlog](docs/tasks/backlog.md)
- [Domain Glossary](docs/context/domain-glossary.md)
- [Prompt History](prompt-history.md) · [Prompt History Report](prompt-history-report.md)
