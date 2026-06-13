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

- **Video demo:** [Video Demo.mp4](https://tinhvan-my.sharepoint.com/personal/trangnth2_tinhvan_com/_layouts/15/stream.aspx?id=%2Fpersonal%2Ftrangnth2%5Ftinhvan%5Fcom%2FDocuments%2FVideo%20Demo%2Emp4&ga=1&referrer=StreamWebApp%2EWeb&referrerScenario=AddressBarCopied%2Eview%2E6477dd77%2Ddd37%2D4df1%2Da70e%2D5be4818748df)
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
