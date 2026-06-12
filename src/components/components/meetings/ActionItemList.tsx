import { PlusIcon } from '@heroicons/react/24/outline'
import { ActionItemRow, type ActionItemDraft } from './ActionItemRow'

interface ActionItemListProps {
  items: ActionItemDraft[]
  onChange: (items: ActionItemDraft[]) => void
  readOnly: boolean
}

export function ActionItemList({ items, onChange, readOnly }: ActionItemListProps) {
  function updateItem(index: number, next: ActionItemDraft) {
    onChange(items.map((item, i) => (i === index ? next : item)))
  }

  function removeItem(index: number) {
    onChange(items.filter((_, i) => i !== index))
  }

  function addItem() {
    onChange([...items, { description: '', owner: '', deadline: '' }])
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium text-slate-900">Next Actions</h2>
        {!readOnly && (
          <button
            type="button"
            onClick={addItem}
            className="inline-flex items-center gap-1.5 text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors duration-150"
          >
            <PlusIcon className="h-4 w-4" />
            Add item
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <p className="text-sm text-slate-500 py-4 text-center border border-dashed border-slate-200 rounded-lg">
          No action items yet.
        </p>
      ) : (
        <div className="space-y-3">
          {items.map((item, index) => (
            <ActionItemRow
              key={item.id ?? `new-${index}`}
              item={item}
              index={index}
              onChange={updateItem}
              onRemove={removeItem}
              readOnly={readOnly}
            />
          ))}
        </div>
      )}
    </div>
  )
}
