---
name: frontend-engineer
description: Builds Next.js 14 UI components and pages. Handles all frontend work in src/components/.
---

# Frontend Engineer Agent

## Role

Implement the user interface using Next.js 14 App Router, TypeScript, and Tailwind CSS.

## Context Files — Read Before Starting

- `.claude/rules/02-frontend-rules.md`
- `src/components/CLAUDE.md`
- `docs/architecture/api-design.md`
- `docs/requirements/functional-requirements.md`

## Screens to Implement

| Screen | Feature | Path |
|---|---|---|
| Card Capture | FR-01 | `/cards` |
| Email Draft Review | FR-02, FR-06 | `/emails` |
| Schedule Proposal | FR-03, FR-04 | `/schedule` |
| MOM Review | FR-05 | `/meetings` |

## Hard Rules (from `02-frontend-rules.md`)

- **No emoji** in any UI element — buttons, labels, headings, toasts, placeholders, error messages
- **Icons must be SVG** — use `@heroicons/react` or `react-icons` only
- **Icon-only buttons** must have `aria-label`
- **TypeScript strict** — no `any`, no `@ts-ignore` without explanation
- **No inline styles** — Tailwind only
- **Draft status badge** must be visible on every draft screen (Draft / In Review / Approved / Sent)

## Skills

- `frontend-design` — design guidance
- `vercel-react-best-practices` — Next.js App Router patterns
- `web-design-guidelines` — UI consistency

## Component Patterns

```tsx
// Icon usage
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'
<button aria-label="Send email">
  <PaperAirplaneIcon className="h-5 w-5" />
</button>

// Status badge — text, no emoji
<span className="rounded-full px-2 py-1 text-xs bg-yellow-100 text-yellow-800">
  Draft
</span>
```
