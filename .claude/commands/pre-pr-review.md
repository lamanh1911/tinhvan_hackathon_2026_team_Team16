# /pre-pr-review

Run the full review checklist from `06-review-checklist.md` before creating a pull request.

## Steps

1. Run `/frontend-check` — must pass
2. Run `/backend-check` — must pass
3. Run `/test-all` — all tests must pass
4. Run `/railway-check` — must pass
5. Check each item in `.claude/rules/06-review-checklist.md` manually:
   - Human-in-the-loop rules intact
   - No PII in logs
   - No hardcoded secrets
   - Alembic migration present if schema changed
   - Migration has downgrade()

## Output

```
## Pre-PR Review

- [ ] /frontend-check: PASS / FAIL
- [ ] /backend-check: PASS / FAIL
- [ ] /test-all: PASS / FAIL
- [ ] /railway-check: PASS / FAIL
- [ ] Manual checklist: PASS / items pending

Blockers: [list any blockers before PR can be created]
```

Do not create a PR if any check fails.
