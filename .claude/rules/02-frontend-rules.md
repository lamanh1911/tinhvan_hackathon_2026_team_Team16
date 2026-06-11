# 02 - Frontend Rules

## Emoji — PROHIBITED

- Do not use emoji in any UI element
- Do not use emoji in: button labels, headings, form labels, toast messages, error messages, placeholder text, tooltips, navigation items, badge text, tab labels
- Do not use emoji as a substitute for icons
- This rule has no exceptions

## Icons — SVG Only

- All icons must be SVG
- Use `heroicons` (via `@heroicons/react`) or `react-icons` as the icon library
- Do not create custom icons using emoji, Unicode symbols, or ASCII characters
- Every icon-only button must have an `aria-label` attribute

```tsx
// Correct
import { PaperAirplaneIcon } from '@heroicons/react/24/outline'
<button aria-label="Send email"><PaperAirplaneIcon className="h-5 w-5" /></button>

// Wrong
<button>✉️ Send</button>
<button>→</button>
```

## TypeScript

- Strict mode is enabled — do not disable it
- No `any` type — use `unknown` and narrow, or define a proper type
- No `@ts-ignore` without a written explanation in the same comment
- All API response types must be defined and match the Pydantic schemas in `src/api/schemas/`

## Styling

- Use Tailwind CSS utility classes
- No inline styles (`style={{ ... }}`)
- No CSS modules unless there is a specific reason documented in the component
- Responsive design is required for all screens

## Component Structure

- One component per file
- File name matches the component name (PascalCase)
- Do not mix data-fetching logic and rendering in the same component
- Use React Server Components for data fetching where possible (Next.js App Router)

## Draft Status Display

- Every email draft or MOM must display its current status badge: Draft / In Review / Approved / Sent
- Status badges use colors — no emoji
- Send and Approve buttons are only enabled when the draft is in the correct state

## Accessibility

- All interactive elements are keyboard-navigable
- All images have `alt` text
- Color alone must not convey meaning — use text or icons alongside color
