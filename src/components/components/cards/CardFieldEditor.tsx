'use client'

import { useEffect, useState } from 'react'
import { ConfidenceIndicator } from './ConfidenceIndicator'
import type { FieldWithConfidence } from '@/lib/types'

interface CardFieldEditorProps {
  fieldName: string
  label: string
  field: FieldWithConfidence
  required?: boolean
  onSave: (fieldName: string, value: string) => Promise<void>
}

export function CardFieldEditor({
  fieldName,
  label,
  field,
  required,
  onSave,
}: CardFieldEditorProps) {
  const [editing, setEditing] = useState(false)
  const [value, setValue] = useState(field.value ?? '')
  const [saving, setSaving] = useState(false)
  const [saveError, setSaveError] = useState<string | null>(null)

  console.log(`[STEP 3] confirm screen — field "${fieldName}": value=${JSON.stringify(field.value)} confidence=${field.confidence} flagged=${field.flagged}`)

  // Sync input value when prop changes from parent (e.g. after patch response)
  useEffect(() => {
    if (!editing) {
      setValue(field.value ?? '')
    }
  }, [field.value, editing])

  const isFlagged = field.flagged || !field.value

  async function handleSave() {
    if (!value.trim()) return
    setSaving(true)
    setSaveError(null)
    try {
      await onSave(fieldName, value.trim())
      setEditing(false)
    } catch {
      setSaveError('Save failed')
    } finally {
      setSaving(false)
    }
  }

  function handleCancel() {
    setEditing(false)
    setValue(field.value ?? '')
    setSaveError(null)
  }

  const inputId = `field-${fieldName}`

  return (
    <div
      className={`p-4 rounded-lg border transition-colors duration-150 ${
        isFlagged ? 'border-amber-400 bg-amber-50' : 'border-slate-200 bg-white'
      }`}
    >
      <div className="flex items-center justify-between mb-2">
        <label
          htmlFor={inputId}
          className="text-xs font-medium text-slate-500 uppercase tracking-wide"
        >
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
        <ConfidenceIndicator
          confidence={field.confidence}
          flagged={field.flagged}
          value={field.value}
        />
      </div>

      {editing ? (
        <div className="space-y-2">
          <div className="flex gap-2">
            <input
              id={inputId}
              type="text"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={`Enter ${label}`}
              title={label}
              className="flex-1 text-sm text-slate-900 border border-slate-300 rounded-md px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
              onKeyDown={(e) => {
                if (e.key === 'Enter') handleSave()
                if (e.key === 'Escape') handleCancel()
              }}
            />
            <button
              type="button"
              onClick={handleSave}
              disabled={saving || !value.trim()}
              className="text-xs font-medium text-white bg-blue-600 hover:bg-blue-700 px-3 py-1.5 rounded-md disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-150"
            >
              {saving ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              className="text-xs font-medium text-slate-600 hover:text-slate-900 px-3 py-1.5 rounded-md border border-slate-200 hover:border-slate-300 transition-colors duration-150"
            >
              Cancel
            </button>
          </div>
          {saveError && <p className="text-xs text-red-600">{saveError}</p>}
        </div>
      ) : (
        <div className="flex items-center justify-between group">
          <span
            className={`text-sm ${
              field.value ? 'text-slate-900' : 'text-slate-400 italic'
            }`}
          >
            {field.value ?? 'Not detected'}
          </span>
          <button
            type="button"
            aria-label={`Edit ${label}`}
            onClick={() => setEditing(true)}
            className={`text-xs text-blue-600 hover:text-blue-700 transition-opacity duration-150 shrink-0 ml-3 ${
              isFlagged ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'
            }`}
          >
            Edit
          </button>
        </div>
      )}
    </div>
  )
}
