# /test-all

Run the full test suite and report results.

## Steps

1. Run backend unit tests:
   ```bash
   cd src/api
   pytest tests/unit/ -v
   ```

2. Run backend integration tests:
   ```bash
   pytest tests/integration/ -v
   ```

3. Run frontend E2E tests:
   ```bash
   cd src/components
   npx playwright test
   ```

4. Report:
   - Total tests run
   - Passed / Failed / Skipped
   - For each failure: test name, error message, file and line

## Pass Criteria

All tests must pass before any deployment or PR creation. Do not proceed if any test fails — investigate and fix first.
