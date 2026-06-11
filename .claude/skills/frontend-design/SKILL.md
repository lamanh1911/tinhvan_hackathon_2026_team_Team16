---
name: frontend-design
description: Relay App design system for AI Sales Follow-up Assistant. Use when building any screen, component, or layout in src/components/. Covers Relay color tokens, typography, spacing, component patterns, and per-feature UX rules. Single source of truth for all UI decisions.
metadata:
  type: project-skill
  version: "2.0.0"
---

# Frontend Design — Relay App Design System

Single source of truth for all UI work in `src/components/`.
Read this before building any screen or component. Do not duplicate with `ui-designer` (deleted).

## Design Token Reference

Full token definitions live in `.claude/rules/02-frontend-rules.md` → "Design System — Relay App" section.
This skill references those tokens; it does not repeat them.

---

## Component Mapping

Each pattern below maps to a file path in `src/components/`.

### Button

```tsx
// Primary
<button className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed">
  Label
</button>

// Secondary
<button className="bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed">
  Label
</button>

// Danger
<button className="bg-red-600 text-white hover:bg-red-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed">
  Label
</button>

// Icon-only — always needs aria-label
<button aria-label="Send email" className="p-2 rounded-md hover:bg-slate-100 transition-colors duration-150">
  <PaperAirplaneIcon className="h-5 w-5 text-slate-600" />
</button>
```

### Card / Dashboard Card

```tsx
// Standard card
<div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
  <h2 className="text-lg font-medium text-slate-900 mb-4">Title</h2>
  {children}
</div>

// Dashboard stat card
<div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 flex flex-col gap-1">
  <p className="text-xs text-slate-500 uppercase tracking-wide">Label</p>
  <p className="text-2xl font-semibold text-slate-900">Value</p>
</div>
```

### Form Fields

```tsx
// Text input
<div className="space-y-1">
  <label className="block text-sm font-medium text-slate-700">{label}</label>
  <input
    className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm
               focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none
               disabled:bg-slate-100 disabled:text-slate-400 transition-colors duration-150"
  />
  <p className="text-xs text-slate-500">{helperText}</p>
</div>

// Flagged field (confidence < 0.7) — amber
<input className="... border-amber-400 bg-amber-50 focus:border-amber-500 focus:ring-amber-500" />
<p className="text-xs text-amber-600">Needs review — please verify this field</p>

// Missing required field — red
<input className="... border-red-400 bg-red-50 focus:border-red-500 focus:ring-red-500" />
<p className="text-xs text-red-600">This field is required</p>

// Select
<select className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm
                   focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none bg-white">

// Textarea
<textarea className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm
                     focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none" />

// Checkbox
<label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
  <input type="checkbox" className="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
  {label}
</label>
```

### Table

```tsx
<div className="overflow-hidden rounded-lg border border-slate-200">
  <table className="min-w-full divide-y divide-slate-200">
    <thead className="bg-slate-50">
      <tr>
        <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
          Column
        </th>
      </tr>
    </thead>
    <tbody className="divide-y divide-slate-100 bg-white">
      <tr className="hover:bg-slate-50 transition-colors duration-150">
        <td className="px-4 py-3 text-sm text-slate-900">Cell</td>
      </tr>
    </tbody>
  </table>
</div>
```

### Modal / Dialog

```tsx
// Overlay + dialog
<div className="fixed inset-0 z-50 flex items-center justify-center">
  <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm" onClick={onClose} />
  <div className="relative z-10 bg-white rounded-lg shadow-md w-full max-w-md p-6 space-y-4">
    <h2 className="text-lg font-medium text-slate-900">Title</h2>
    <div className="text-sm text-slate-600">{content}</div>
    <div className="flex justify-end gap-3 pt-2">
      <button className="... secondary ...">Cancel</button>
      <button className="... primary ...">Confirm</button>
    </div>
  </div>
</div>
```

### Confirmation Dialog

Same as Modal but content is a single sentence question.
Confirm button uses Danger variant when the action is destructive.

### Status Badge

`src/components/ui/StatusBadge.tsx`

```tsx
const STATUS_STYLES = {
  draft:     'bg-amber-100 text-amber-800',
  in_review: 'bg-blue-100 text-blue-800',
  approved:  'bg-green-100 text-green-800',
  sent:      'bg-slate-100 text-slate-700',
  rejected:  'bg-red-100 text-red-800',
} as const

type Status = keyof typeof STATUS_STYLES

const STATUS_LABELS: Record<Status, string> = {
  draft: 'Draft', in_review: 'In Review', approved: 'Approved',
  sent: 'Sent', rejected: 'Rejected',
}

export function StatusBadge({ status }: { status: Status }) {
  return (
    <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status]}`}>
      {STATUS_LABELS[status]}
    </span>
  )
}
```

### Confidence Indicator (FR-01)

`src/components/ui/ConfidenceIndicator.tsx`

```tsx
export function ConfidenceIndicator({ confidence }: { confidence: number | null }) {
  if (confidence === null) return <span className="text-xs font-medium text-red-600">Required</span>
  if (confidence >= 0.7)   return <span className="text-xs font-medium text-green-600">Accepted</span>
  return <span className="text-xs font-medium text-amber-600">Needs review</span>
}
```

### Sidebar Navigation

`src/components/layout/Sidebar.tsx`

```tsx
// Active item: blue-600 text + blue-50 bg
// Inactive: slate-600 text, hover:bg-slate-50
<nav className="w-64 bg-white border-r border-slate-200 h-full py-4">
  <a href="/cards" className="flex items-center gap-3 px-4 py-2.5 text-sm font-medium
                               text-blue-600 bg-blue-50 rounded-md mx-2">
    <IdentificationIcon className="h-5 w-5" />
    Card Scan
  </a>
  <a href="/emails" className="flex items-center gap-3 px-4 py-2.5 text-sm font-medium
                                text-slate-600 hover:bg-slate-50 rounded-md mx-2 transition-colors">
    <EnvelopeIcon className="h-5 w-5" />
    Emails
  </a>
</nav>
```

Nav items (SVG icons only — no emoji):

| Label | Route | Icon |
|---|---|---|
| Card Scan | `/cards` | `IdentificationIcon` |
| Emails | `/emails` | `EnvelopeIcon` |
| Schedule | `/schedule` | `CalendarIcon` |
| Meetings | `/meetings` | `DocumentTextIcon` |

### Top Navigation / Header

```tsx
<header className="h-[60px] bg-white border-b border-slate-200 flex items-center px-6 gap-4">
  <span className="text-lg font-semibold text-slate-900">Relay</span>
  <div className="flex-1" />
  {/* Right side: user avatar or actions */}
</header>
```

### Tabs

```tsx
<div className="border-b border-slate-200 flex gap-1">
  {/* Active tab */}
  <button className="px-4 py-2 text-sm font-medium text-blue-600 border-b-2 border-blue-600 -mb-px">
    Tab Label
  </button>
  {/* Inactive tab */}
  <button className="px-4 py-2 text-sm font-medium text-slate-500 hover:text-slate-700 border-b-2 border-transparent -mb-px transition-colors">
    Tab Label
  </button>
</div>
```

### Search Bar

```tsx
<div className="relative">
  <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
  <input
    type="search"
    placeholder="Search..."
    className="w-full pl-9 pr-4 py-2 text-sm border border-slate-300 rounded-md
               focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
  />
</div>
```

### Toast / Feedback

```tsx
// Success
<div role="status" className="flex items-center gap-3 bg-green-50 border border-green-200 text-green-800 rounded-lg px-4 py-3 text-sm shadow-sm">
  <CheckCircleIcon className="h-5 w-5 text-green-600 shrink-0" />
  {message}
</div>

// Error
<div role="alert" className="flex items-center gap-3 bg-red-50 border border-red-200 text-red-800 rounded-lg px-4 py-3 text-sm shadow-sm">
  <ExclamationCircleIcon className="h-5 w-5 text-red-600 shrink-0" />
  {message}
</div>
```

### Avatar / Profile Item

```tsx
// Avatar initials fallback
<div className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-semibold shrink-0">
  {initials}
</div>

// Profile row (e.g., customer card header)
<div className="flex items-center gap-3">
  <Avatar initials={initials} />
  <div>
    <p className="text-sm font-medium text-slate-900">{name}</p>
    <p className="text-xs text-slate-500">{company}</p>
  </div>
</div>
```

### Pagination

```tsx
<div className="flex items-center justify-between py-3 text-sm text-slate-600">
  <p>Showing {from}–{to} of {total}</p>
  <div className="flex gap-1">
    <button className="px-3 py-1.5 border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
      Previous
    </button>
    <button className="px-3 py-1.5 border border-slate-300 rounded-md hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
      Next
    </button>
  </div>
</div>
```

### Empty State

```tsx
<div className="flex flex-col items-center justify-center py-16 text-center">
  <SomeOutlineIcon className="h-12 w-12 text-slate-300 mb-4" />
  <p className="text-sm font-medium text-slate-900 mb-1">No items yet</p>
  <p className="text-xs text-slate-500 mb-4">Description of what to do next.</p>
  <button className="... primary ...">Primary Action</button>
</div>
```

### Loading State

```tsx
// Inline spinner
<svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
</svg>

// Skeleton card
<div className="bg-white rounded-lg border border-slate-200 p-6 animate-pulse space-y-3">
  <div className="h-4 bg-slate-200 rounded w-1/3" />
  <div className="h-3 bg-slate-100 rounded w-2/3" />
  <div className="h-3 bg-slate-100 rounded w-1/2" />
</div>
```

### Draft Action Buttons (State Machine)

Buttons are enabled/disabled based on current draft status:

```tsx
// Approve — enabled in draft or in_review only
<button
  onClick={onApprove}
  disabled={!['draft', 'in_review'].includes(status)}
  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium
             hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
>
  Approve
</button>

// Send — enabled only when approved
<button
  onClick={onSend}
  disabled={status !== 'approved'}
  className="bg-green-600 text-white px-4 py-2 rounded-md text-sm font-medium
             hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
>
  Send
</button>
```

### Page Shell

Standard wrapper for all feature pages:

```tsx
export default function PageShell({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="px-6 py-8 max-w-[1200px]">
      <h1 className="text-2xl font-semibold text-slate-900 mb-6">{title}</h1>
      {children}
    </div>
  )
}
```

---

## Screen UX Flows (per Feature)

### FR-01 — Business Card Scan (`/cards`)

1. `/cards` — upload page: drag-drop zone + "Upload and Scan" button
2. `/cards/[id]` — field review: form with ConfidenceIndicator per field + StatusBadge (Draft) + "Confirm and Save" button (disabled if required fields missing or flagged red)

### FR-02 — Thank-you Email Draft (`/emails`)

1. `/emails` — list view: table of drafts with StatusBadge column
2. `/emails/[id]` — draft view: editable textarea + StatusBadge + Approve/Send buttons (state machine)

### FR-03 / FR-04 — Meeting Schedule Proposal (`/schedule`)

1. `/schedule/[meetingId]` — calendar availability display + propose slots form
2. Confirmation step before sending proposal

### FR-05 — MOM Review (`/meetings`)

1. `/meetings` — list: table of meetings with MOM status
2. `/meetings/[id]` — MOM detail: summary + action items list + StatusBadge + Approve button

### FR-06 — Follow-up Email Draft (`/emails`)

Same routes as FR-02 but `type = follow_up`. AttachmentSuggestions component shown below the draft textarea.

```tsx
export function AttachmentSuggestions({ suggestions }: { suggestions: string[] }) {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium text-slate-700">Suggested Attachments</p>
      {suggestions.map((name) => (
        <label key={name} className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
          <input type="checkbox" className="rounded border-slate-300 text-blue-600 focus:ring-blue-500" />
          {name}
        </label>
      ))}
    </div>
  )
}
```

---

## Rules (non-negotiable)

- No emoji anywhere — buttons, labels, headings, toasts, badges, placeholders
- All icons: SVG from `@heroicons/react` or `react-icons`
- Icon-only buttons must have `aria-label`
- StatusBadge must be visible on every draft screen
- No inline styles — Tailwind only
- TypeScript strict — no `any`

## Related Skills

- `vercel-react-best-practices` — Next.js App Router performance patterns
- `web-design-guidelines` — accessibility and UX compliance audit
