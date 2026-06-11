interface ConfidenceIndicatorProps {
  confidence: number | null
  flagged: boolean
  value?: string | null
}

export function ConfidenceIndicator({ confidence, flagged, value }: ConfidenceIndicatorProps) {
  if (value === null || value === undefined || value === '') {
    return (
      <span className="text-xs font-medium text-red-600 bg-red-50 px-2 py-0.5 rounded-full border border-red-200">
        Missing
      </span>
    )
  }
  if (flagged || confidence === null || confidence < 0.7) {
    return (
      <span className="text-xs font-medium text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
        Low
      </span>
    )
  }
  return (
    <span className="text-xs font-medium text-green-600 bg-green-50 px-2 py-0.5 rounded-full border border-green-200">
      High
    </span>
  )
}
