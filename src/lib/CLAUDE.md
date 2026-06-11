# src/lib/ - Shared Utilities

Shared TypeScript types and utilities used by the frontend (`components/`).

## Contents (to be created)

```
lib/
  types.ts        TypeScript types mirroring the Pydantic schemas in src/api/schemas/
  api-client.ts   Fetch wrapper for calling the FastAPI backend
  constants.ts    Shared constants (status values, routes, etc.)
```

## Rules

- Types in `types.ts` must stay in sync with Pydantic schemas in `src/api/schemas/`
- `api-client.ts` handles: base URL config, JSON parsing, error normalization
- No business logic here — lib is for shared infrastructure only
