import { TrashIcon } from '@heroicons/react/24/outline'

export interface ActionItemDraft {
  id?: string
  description: string
  owner: string
  deadline: string
}

interface ActionItemRowProps {
  item: ActionItemDraft
  index: number
  onChange: (index: number, item: ActionItemDraft) => void
  onRemove: (index: number) => void
  readOnly: boolean
}

export function ActionItemRow({
  item,
  index,
  onChange,
  onRemove,
  readOnly,
}: ActionItemRowProps) {
  const ownerMissing = item.owner.trim() === ''
  const deadlineMissing = item.deadline.trim() === ''

  function update(field: keyof ActionItemDraft, value: string) {
    onChange(index, { ...item, [field]: value })
  }

  const fieldBase =
    'block w-full rounded-md border px-3 py-2 text-sm outline-none transition-colors duration-150 ' +
    'read-only:bg-slate-100 read-only:text-slate-600'
  const normalBorder = 'border-slate-300 focus:border-blue-500 focus:ring-1 focus:ring-blue-500'
  const errorBorder = 'border-red-400 bg-red-50 focus:border-red-500 focus:ring-1 focus:ring-red-500'

  return (
    <div className="rounded-lg border border-slate-200 p-4 space-y-3">
      <div className="flex items-start gap-3">
        <div className="flex-1 space-y-1">
          <label className="block text-xs font-medium text-slate-600">Description</label>
          <input
            value={item.description}
            onChange={(e) => update('description', e.target.value)}
            readOnly={readOnly}
            placeholder="What needs to be done"
            className={`${fieldBase} ${
              item.description.trim() === '' && !readOnly ? errorBorder : normalBorder
            }`}
          />
        </div>
        {!readOnly && (
          <button
            type="button"
            onClick={() => onRemove(index)}
            aria-label="Remove action item"
            className="mt-6 p-2 rounded-md text-slate-400 hover:bg-slate-100 hover:text-red-600 transition-colors duration-150"
          >
            <TrashIcon className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <label className="block text-xs font-medium text-slate-600">Owner</label>
          <input
            value={item.owner}
            onChange={(e) => update('owner', e.target.value)}
            readOnly={readOnly}
            placeholder="Responsible person"
            className={`${fieldBase} ${ownerMissing && !readOnly ? errorBorder : normalBorder}`}
          />
          {ownerMissing && !readOnly && (
            <p className="text-xs text-red-600">Owner is required</p>
          )}
        </div>
        <div className="space-y-1">
          <label className="block text-xs font-medium text-slate-600">Deadline</label>
          <input
            type="date"
            value={item.deadline}
            onChange={(e) => update('deadline', e.target.value)}
            readOnly={readOnly}
            className={`${fieldBase} ${deadlineMissing && !readOnly ? errorBorder : normalBorder}`}
          />
          {deadlineMissing && !readOnly && (
            <p className="text-xs text-red-600">Deadline is required</p>
          )}
        </div>
      </div>
    </div>
  )
}
