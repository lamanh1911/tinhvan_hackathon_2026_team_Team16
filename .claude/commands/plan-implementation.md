# /plan-implementation

Create an implementation plan for a feature before writing any code.

## Steps

1. Read `docs/requirements/functional-requirements.md` — find the relevant FR
2. Read `docs/architecture/api-design.md` and `docs/architecture/database-design.md`
3. Read `.claude/rules/00-project-policy.md` and the relevant tech rules (02, 03, 04)
4. Produce a written plan with:
   - Files to create or modify
   - Database changes needed (if any)
   - API endpoints to add or change
   - Frontend components to create or modify
   - External integrations involved
   - Acceptance criteria from the FR
5. Present the plan — do not write any code until approved

## Output Format

```
## Plan: [Feature Name] (FR-XX)

### Files Changed
- `src/api/routers/...` — [reason]
- `src/components/...` — [reason]

### Database Changes
- Migration: [description]

### API Endpoints
- POST /endpoint — [purpose]

### Acceptance Criteria
- [ ] criterion 1
- [ ] criterion 2
```
