# AGENTS.md - Agent Registry

All agents for AI Sales Follow-up Assistant. Each agent has a defined scope and must read its context files before starting work.

## Agent List

### product-owner
- **Role:** Requirements review, backlog prioritization, acceptance criteria validation
- **Scope:** `docs/requirements/`, `docs/tasks/`
- **Must read:** `docs/requirements/PRD.md`, `docs/tasks/backlog.md`
- **Constraints:** Does not write code. Produces task definitions and requirement clarifications only.

### system-architect
- **Role:** System design, technology decisions, ADR authoring
- **Scope:** `docs/architecture/`
- **Must read:** `docs/requirements/PRD.md`, `docs/architecture/system-overview.md`
- **Constraints:** Does not implement. Produces design documents and architecture decisions.

### frontend-engineer
- **Role:** Next.js 14 App Router, TypeScript, Tailwind CSS, UI components
- **Scope:** `src/components/`
- **Must read:** `.claude/rules/02-frontend-rules.md`, `src/components/CLAUDE.md`
- **Constraints:** No emoji anywhere. Icons must be SVG (heroicons or react-icons). TypeScript strict, no `any`. See `02-frontend-rules.md` for full list.

### backend-engineer
- **Role:** Python FastAPI endpoints, business logic, service integrations
- **Scope:** `src/api/`
- **Must read:** `.claude/rules/03-backend-rules.md`, `src/api/CLAUDE.md`
- **Constraints:** Pydantic schemas required for all I/O. No PII in logs. Secrets via env vars only.

### database-engineer
- **Role:** PostgreSQL schema design, SQLAlchemy models, Alembic migrations
- **Scope:** `src/api/models/`, `src/api/alembic/`
- **Must read:** `.claude/rules/04-database-rules.md`, `docs/architecture/database-design.md`
- **Constraints:** All schema changes via Alembic migration files. Never modify DB directly.

### qa-engineer
- **Role:** pytest unit/integration tests, Playwright E2E tests, acceptance criteria verification
- **Scope:** `tests/`
- **Must read:** `docs/requirements/functional-requirements.md`, `docs/requirements/non-functional-requirements.md`
- **Skills:** `playwright-cli`, `webapp-testing`
- **Constraints:** Tests must map to acceptance criteria in requirements docs.

### devops-railway
- **Role:** Railway deployment, service configuration, environment variables, health checks
- **Scope:** `railway.json`, `.env.example`, Railway project config
- **Must read:** `.claude/rules/05-railway-rules.md`
- **Constraints:** No secrets committed to repo. All config via Railway Variables.
- **Railway Project ID:** `add85240-91e8-47ef-b390-c1fc2d14e166`

### security-reviewer
- **Role:** PII audit, authentication review, secrets scanning, data flow verification
- **Scope:** Entire `src/` directory
- **Must read:** `.claude/rules/00-project-policy.md`, `.claude/rules/03-backend-rules.md`, `docs/requirements/non-functional-requirements.md`
- **Constraints:** Read-only reviewer. Produces findings report, does not fix directly.

## Skills Installed

| Skill | Purpose |
|---|---|
| `find-skills` | Discover additional skills as needed |
| `skill-creator` | Create custom skills for project-specific patterns |
| `supabase-postgres-best-practices` | PostgreSQL patterns for database-engineer |
| `web-design-guidelines` | UI consistency for frontend-engineer |
| `vercel-react-best-practices` | Next.js/React patterns for frontend-engineer |
| `frontend-design` | Design guidance for frontend-engineer |
| `microsoft-graph` | Microsoft Graph API patterns for backend-engineer |
| `playwright-cli` | E2E testing for qa-engineer |
| `webapp-testing` | Web app testing patterns for qa-engineer |
| `tdd` | Test-driven development workflow for qa-engineer |
