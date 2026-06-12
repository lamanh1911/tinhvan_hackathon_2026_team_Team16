import { CheckCircleIcon } from '@heroicons/react/24/outline'

interface MOMActionsProps {
  isApproved: boolean
  canApprove: boolean
  saving: boolean
  approving: boolean
  onSave: () => void
  onApprove: () => void
}

export function MOMActions({
  isApproved,
  canApprove,
  saving,
  approving,
  onSave,
  onApprove,
}: MOMActionsProps) {
  if (isApproved) {
    return (
      <p className="flex items-center gap-1.5 text-sm text-green-700 bg-green-50 border border-green-200 rounded-md px-3 py-2">
        <CheckCircleIcon className="h-4 w-4 text-green-600 shrink-0" />
        Minutes approved — you can now generate a follow-up email.
      </p>
    )
  }

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={onSave}
        disabled={saving || approving}
        className="bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {saving ? 'Saving...' : 'Save changes'}
      </button>
      <button
        type="button"
        onClick={onApprove}
        disabled={!canApprove || saving || approving}
        className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {approving ? 'Approving...' : 'Approve Minutes'}
      </button>
    </div>
  )
}
