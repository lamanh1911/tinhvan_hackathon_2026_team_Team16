'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { EnvelopeIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { EmailDraft } from '@/lib/types'

const TYPE_LABELS: Record<EmailDraft['type'], string> = {
  thank_you: 'Thank-you',
  follow_up: 'Follow-up',
}

export default function EmailsPage() {
  const [emails, setEmails] = useState<EmailDraft[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchEmails = useCallback(async () => {
    setError(null)
    try {
      const data = await api.get<EmailDraft[]>('/emails')
      setEmails(data)
    } catch (err) {
      setError(err instanceof ApiRequestError ? err.message : 'Failed to load emails')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchEmails()
  }, [fetchEmails])

  return (
    <div className="px-6 py-8 max-w-[1200px]">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Emails</h1>
        <p className="text-sm text-slate-500 mt-1">
          Review email drafts, submit for approval, then mark as sent.
        </p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
        </div>
      ) : error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : emails.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <EnvelopeIcon className="h-12 w-12 text-slate-300 mb-4" />
          <p className="text-sm font-medium text-slate-900 mb-1">No emails yet</p>
          <p className="text-xs text-slate-500">
            Generate a follow-up email from an approved set of meeting minutes.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Subject
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Type
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Status
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wide">
                  <span className="sr-only">Open</span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 bg-white">
              {emails.map((email) => (
                <tr
                  key={email.id}
                  className="hover:bg-slate-50 transition-colors duration-150"
                >
                  <td className="px-4 py-3 text-sm text-slate-900 max-w-md">
                    <span className="line-clamp-1">
                      {email.subject ?? 'Untitled draft'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {TYPE_LABELS[email.type]}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <StatusBadge status={email.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/emails/${email.id}`}
                      className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors duration-150"
                    >
                      Open
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
