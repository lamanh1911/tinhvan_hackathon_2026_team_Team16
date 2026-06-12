interface MOMSummaryProps {
  value: string
  onChange: (value: string) => void
  readOnly: boolean
}

export function MOMSummary({ value, onChange, readOnly }: MOMSummaryProps) {
  return (
    <div className="space-y-1">
      <label htmlFor="mom-summary" className="block text-sm font-medium text-slate-700">
        Discussion Summary
      </label>
      <textarea
        id="mom-summary"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        readOnly={readOnly}
        rows={6}
        placeholder="Main discussion points from the meeting"
        className="block w-full rounded-md border border-slate-300 px-3 py-2 text-sm
                   focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none
                   read-only:bg-slate-100 read-only:text-slate-600 transition-colors duration-150"
      />
      {value.trim() === '' && !readOnly && (
        <p className="text-xs text-red-600">A summary is required</p>
      )}
    </div>
  )
}
