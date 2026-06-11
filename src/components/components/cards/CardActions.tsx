import { CheckCircleIcon } from '@heroicons/react/24/outline'
import type { CardScanResponse } from '@/lib/types'

const REQUIRED_FIELDS = ['name', 'company', 'email'] as const

interface CardActionsProps {
  card: CardScanResponse
  confirming: boolean
  onConfirm: () => void
}

export function CardActions({ card, confirming, onConfirm }: CardActionsProps) {
  const blockers = REQUIRED_FIELDS.filter((field) => {
    const f = card.fields[field]
    return !f?.value || f.flagged
  })

  const isConfirmed = card.status === 'confirmed'
  const canConfirm = blockers.length === 0 && !isConfirmed

  return (
    <div className="space-y-3">
      {blockers.length > 0 && (
        <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
          Required fields need correction before confirming:{' '}
          <span className="font-medium">{blockers.join(', ')}</span>
        </p>
      )}

      {isConfirmed && (
        <p className="text-xs text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-2 flex items-center gap-1.5">
          <CheckCircleIcon className="h-4 w-4 text-green-600 shrink-0" />
          Card confirmed — customer record created successfully
        </p>
      )}

      <button
        onClick={onConfirm}
        disabled={!canConfirm || confirming}
        className="w-full flex items-center justify-center gap-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 px-4 py-2.5 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
      >
        {confirming ? (
          <>
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
            Confirming...
          </>
        ) : (
          <>
            <CheckCircleIcon className="h-4 w-4" />
            Confirm Card
          </>
        )}
      </button>
    </div>
  )
}
