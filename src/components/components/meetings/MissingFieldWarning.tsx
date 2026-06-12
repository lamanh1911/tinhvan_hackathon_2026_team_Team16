import { ExclamationTriangleIcon } from '@heroicons/react/24/outline'

interface MissingFieldWarningProps {
  messages: string[]
}

export function MissingFieldWarning({ messages }: MissingFieldWarningProps) {
  if (messages.length === 0) return null

  return (
    <div
      role="alert"
      className="flex items-start gap-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg px-4 py-3 text-sm"
    >
      <ExclamationTriangleIcon className="h-5 w-5 text-amber-600 shrink-0 mt-0.5" />
      <div>
        <p className="font-medium">Complete the following before approving:</p>
        <ul className="list-disc list-inside mt-1 space-y-0.5">
          {messages.map((message) => (
            <li key={message}>{message}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
