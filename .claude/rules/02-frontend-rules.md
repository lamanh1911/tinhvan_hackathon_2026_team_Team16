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

---

## Design System — Relay App (Single Source of Truth)

All visual decisions derive from the Relay App design. Do not invent tokens outside this table.

### Color Palette

| Token | Tailwind class | Hex | Usage |
|---|---|---|---|
| Brand primary | `blue-600` | `#2563eb` | Primary buttons, active nav, links |
| Brand hover | `blue-700` | `#1d4ed8` | Hover state for primary actions |
| Brand active | `blue-800` | `#1e40af` | Active/pressed state |
| Focus ring | `blue-500` | `#3b82f6` | Focus outline on inputs |
| Surface default | `white` | `#ffffff` | Card and panel backgrounds |
| Surface page | `slate-50` | `#f8fafc` | Page background |
| Surface subtle | `slate-100` | `#f1f5f9` | Disabled fields, table header bg |
| Border default | `slate-200` | `#e2e8f0` | Card borders, dividers |
| Border muted | `slate-300` | `#cbd5e1` | Input borders |
| Text primary | `slate-900` | `#0f172a` | Main body text, headings |
| Text secondary | `slate-600` | `#475569` | Labels, metadata |
| Text muted | `slate-500` | `#64748b` | Helper text, captions |
| Text disabled | `slate-400` | `#94a3b8` | Disabled state text |
| Success fg | `green-600` | `#16a34a` | Success messages, approved status |
| Success bg | `green-50` | `#f0fdf4` | Success toast background |
| Warning fg | `amber-600` | `#d97706` | Warnings, needs-review indicator |
| Warning bg | `amber-50` | `#fffbeb` | Warning field highlight |
| Error fg | `red-600` | `#dc2626` | Errors, danger, rejected |
| Error bg | `red-50` | `#fef2f2` | Error state background |

No other brand colors. Do not add purples, teals, or pinks without explicit approval.

### Status Badge Colors

| Status | Background | Text | Tailwind |
|---|---|---|---|
| Draft | amber-100 | amber-800 | `bg-amber-100 text-amber-800` |
| In Review | blue-100 | blue-800 | `bg-blue-100 text-blue-800` |
| Approved | green-100 | green-800 | `bg-green-100 text-green-800` |
| Sent | slate-100 | slate-700 | `bg-slate-100 text-slate-700` |
| Rejected | red-100 | red-800 | `bg-red-100 text-red-800` |

### Confidence Indicator Colors (FR-01)

| Level | Condition | Color | Tailwind |
|---|---|---|---|
| High | confidence ≥ 0.7 | Green | `text-green-600 border-green-300` |
| Low | confidence < 0.7 | Amber | `text-amber-600 border-amber-400` |
| Missing | value absent | Red | `text-red-600 border-red-400` |

### Typography

| Role | Tailwind | Notes |
|---|---|---|
| Page heading | `text-2xl font-semibold text-slate-900` | `<h1>` per page |
| Section heading | `text-lg font-medium text-slate-900` | Card titles, form groups |
| Body | `text-sm text-slate-700` | Form labels, paragraphs |
| Caption | `text-xs text-slate-500` | Helper text, timestamps |
| Badge | `text-xs font-medium` | Status and confidence badges |
| Mono | `font-mono text-sm` | IDs, codes, transcript references |

Font stack: `font-sans` (Inter via Tailwind default).

### Spacing Scale (4px grid)

Standard patterns:
- Page padding: `px-6 py-8`
- Card padding: `p-6`
- Form field gap: `space-y-4`
- Section gap: `space-y-6`
- Inline elements: `gap-2` or `gap-3`

### Layout

```
┌─────────────────────────────────────────────┐
│  Top bar (h-[60px])                         │
├──────────────────┬──────────────────────────┤
│  Sidebar (w-64)  │  Main (flex-1, px-6 py-8)│
│  bg-white        │  bg-slate-50             │
│  border-r        │  max-w-[1200px]          │
└──────────────────┴──────────────────────────┘
```

- Sidebar: `w-64 bg-white border-r border-slate-200`
- Main area: `flex-1 overflow-y-auto bg-slate-50`
- Cards: `bg-white rounded-lg border border-slate-200 shadow-sm`

### Shadows

| Name | Value |
|---|---|
| `shadow-xs` | `0 1px 2px rgba(15,23,42,0.05)` |
| `shadow-sm` | `0 1px 3px rgba(15,23,42,0.08), 0 1px 2px rgba(15,23,42,0.04)` |
| `shadow-md` | `0 4px 12px rgba(15,23,42,0.08), 0 2px 4px rgba(15,23,42,0.04)` |

Default card shadow: `shadow-sm`. Modal: `shadow-md`.

### Border Radius

- Inputs, buttons, badges: `rounded-md` (6px)
- Cards, panels: `rounded-lg` (8px)
- Pills/full-round badges: `rounded-full`

### Motion

- Transitions: `transition-colors duration-150` for color changes
- Easing: `ease-[cubic-bezier(0.2,0,0,1)]`
- Respect `prefers-reduced-motion` — wrap animations in `motion-safe:`
