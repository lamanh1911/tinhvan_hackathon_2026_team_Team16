# /implement-feature

Implement a feature that has an approved task plan.

## Pre-conditions

- A task file exists in `docs/tasks/` for this feature
- The plan has been reviewed and approved
- All dependencies are implemented

## Steps

1. Read the task file in `docs/tasks/`
2. Read `.claude/rules/` files relevant to the feature (frontend, backend, database)
3. Implement one file at a time, in this order:
   - Database models and migration (if needed)
   - Pydantic schemas
   - Service layer (business logic + integrations)
   - API router
   - Frontend component(s)
   - Frontend page
4. After each file: verify it follows the relevant rules
5. Report completion — list files created/modified

## Constraints

- Implement only what is in the approved task — nothing more
- Do not refactor unrelated code
- Do not add fields or endpoints not in the plan
