# 01 - No Auto Implementation

## Rule

Always plan before implementing. Never write code for a task that has not been reviewed and approved.

## Workflow

1. Read relevant docs in `docs/requirements/` and `docs/architecture/`
2. Produce a written plan (task breakdown, file changes, API contracts)
3. Wait for user approval
4. Implement only what was approved — nothing more
5. Report completion, do not proceed to the next task automatically

## What This Prevents

- Scope creep: adding features not asked for
- Refactoring during bug fixes
- Creating files or abstractions not needed for the current task
- Implementing "nice to have" improvements without approval

## Applying Constraints

- Fix only the bug described — do not clean up surrounding code
- Add only the field requested — do not restructure the schema
- Implement only the endpoint specified — do not add related endpoints speculatively
- Three similar lines is better than a premature abstraction
