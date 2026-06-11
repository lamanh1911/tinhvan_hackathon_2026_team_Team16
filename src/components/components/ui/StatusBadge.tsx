import type { DraftStatus } from '@/lib/types'

const STATUS_STYLES: Record<DraftStatus, string> = {
  draft:     'bg-amber-100 text-amber-800',
  in_review: 'bg-blue-100 text-blue-800',
  approved:  'bg-green-100 text-green-800',
  sent:      'bg-slate-100 text-slate-700',
  rejected:  'bg-red-100 text-red-800',
}

const STATUS_LABELS: Record<DraftStatus, string> = {
  draft:     'Draft',
  in_review: 'In Review',
  approved:  'Approved',
  sent:      'Sent',
  rejected:  'Rejected',
}

interface StatusBadgeProps {
  status: DraftStatus
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status]}`}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}
