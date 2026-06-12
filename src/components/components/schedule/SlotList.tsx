'use client'

import { CalendarIcon, CheckCircleIcon } from '@heroicons/react/24/outline'
import type { SlotProposal } from '@/lib/types'

interface SlotListProps {
  slots: SlotProposal[]
  approvedIndex: number | null
  onApprove?: (index: number) => void
  disabled?: boolean
}

function formatSlot(start: string, end: string): string {
  const s = new Date(start)
  const e = new Date(end)
  const dateStr = s.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
  })
  const startTime = s.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  const endTime = e.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  return `${dateStr} · ${startTime} – ${endTime}`
}

export function SlotList({ slots, approvedIndex, onApprove, disabled }: SlotListProps) {
  return (
    <ol className="space-y-4">
      {slots.map((slot) => {
        const isApproved = approvedIndex === slot.index
        return (
          <li
            key={slot.index}
            className={[
              'rounded-lg border p-4',
              isApproved
                ? 'border-green-400 bg-green-50'
                : 'border-slate-200 bg-white',
            ].join(' ')}
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3 min-w-0">
                {isApproved ? (
                  <CheckCircleIcon className="h-5 w-5 text-green-600 shrink-0" aria-hidden="true" />
                ) : (
                  <CalendarIcon className="h-5 w-5 text-slate-400 shrink-0" aria-hidden="true" />
                )}
                <div>
                  <p className="text-sm font-medium text-slate-900">
                    {formatSlot(slot.start, slot.end)}
                  </p>
                  {isApproved && (
                    <span className="inline-block mt-1 text-xs font-medium text-green-700 bg-green-100 rounded-full px-2 py-0.5">
                      Selected
                    </span>
                  )}
                </div>
              </div>

              {onApprove && !isApproved && (
                <button
                  type="button"
                  disabled={disabled || approvedIndex !== null}
                  onClick={() => onApprove(slot.index)}
                  className="shrink-0 rounded-md bg-blue-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-blue-700 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Select
                </button>
              )}
            </div>

            <div className="mt-3">
              <p className="text-xs font-medium text-slate-500 mb-1">Attendees</p>
              <div className="flex flex-wrap gap-2">
                {slot.attendees.map((a) => (
                  <span
                    key={a.email}
                    className={[
                      'inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium',
                      a.status === 'free'
                        ? 'bg-green-100 text-green-700'
                        : 'bg-red-100 text-red-700',
                    ].join(' ')}
                  >
                    {a.name} &mdash; {a.status === 'free' ? 'Free' : 'Busy'}
                  </span>
                ))}
              </div>
            </div>
          </li>
        )
      })}
    </ol>
  )
}
