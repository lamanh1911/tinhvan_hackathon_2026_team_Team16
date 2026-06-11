# /review-docs

Compare current implementation against requirements docs and report gaps.

## Steps

1. Read `docs/requirements/functional-requirements.md`
2. Read `docs/requirements/non-functional-requirements.md`
3. Scan `src/` for each FR implementation
4. Check each acceptance criterion
5. Report: what is implemented, what is missing, what deviates

## Output Format

```
## Docs Review Report

### FR-01: Business Card Digitization
- Status: Implemented / Partial / Missing
- Acceptance criteria:
  - [x] Criterion met
  - [ ] Criterion missing — [file or area to check]

### Deviations
- [description of what differs from spec]
```
