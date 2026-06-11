# src/components/ - Next.js 14 Frontend

## Stack

- Next.js 14 App Router
- TypeScript (strict mode)
- Tailwind CSS
- `@heroicons/react` and `react-icons` for icons

## Rules (from `02-frontend-rules.md`)

### Emoji — PROHIBITED
No emoji in any UI element: buttons, labels, headings, toasts, placeholders, error messages, tooltips, navigation, badges.

### Icons — SVG only
Use `@heroicons/react` or `react-icons`. Every icon-only button requires `aria-label`.

```tsx
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'
<button aria-label="Send email">
  <PaperAirplaneIcon className="h-5 w-5" />
</button>
```

### TypeScript
No `any`. No `@ts-ignore` without explanation. All props typed.

### Styling
Tailwind utility classes only. No inline styles.

## Screens

| Screen | Feature | Route |
|---|---|---|
| Card Capture | FR-01 | `/cards` |
| Email Draft Review | FR-02, FR-06 | `/emails` |
| Schedule Proposal | FR-03, FR-04 | `/schedule` |
| MOM Review | FR-05 | `/meetings` |

## Draft Status Display

Every draft screen must display a status badge with text (no emoji):
- `Draft` — yellow
- `In Review` — blue
- `Approved` — green
- `Sent` — gray
