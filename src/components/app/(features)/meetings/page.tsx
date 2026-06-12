'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { DocumentTextIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { TranscriptUpload } from '@/components/meetings/TranscriptUpload'
import type { MeetingListItem, MeetingMinutes } from '@/lib/types'

export default function MeetingsPage() {
  const router = useRouter()
  const [meetings, setMeetings] = useState<MeetingListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchMeetings = useCallback(async () => {
    setError(null)
    try {
      const data = await api.get<MeetingListItem[]>('/meetings')
      setMeetings(data)
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : 'Failed to load meetings',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchMeetings()
  }, [fetchMeetings])

  function handleMomCreated(mom: MeetingMinutes) {
    router.push(`/meetings/${mom.meeting_id}/mom`)
  }

  return (
    <div className="px-6 py-8 max-w-[1200px]">
      <div className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Meetings</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload a meeting transcript to generate minutes for review.
        </p>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-8">
        <h2 className="text-lg font-medium text-slate-900 mb-4">New Minutes</h2>
        <TranscriptUpload onMomCreated={handleMomCreated} />
      </div>

      <h2 className="text-lg font-medium text-slate-900 mb-4">Recent Minutes</h2>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
        </div>
      ) : error ? (
        <p className="text-sm text-red-600">{error}</p>
      ) : meetings.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <DocumentTextIcon className="h-12 w-12 text-slate-300 mb-4" />
          <p className="text-sm font-medium text-slate-900 mb-1">No minutes yet</p>
          <p className="text-xs text-slate-500">
            Upload a transcript above to create your first set of minutes.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Summary
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Actions
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
              {meetings.map((meeting) => (
                <tr
                  key={meeting.meeting_id}
                  className="hover:bg-slate-50 transition-colors duration-150"
                >
                  <td className="px-4 py-3 text-sm text-slate-900 max-w-md">
                    <span className="line-clamp-1">
                      {meeting.summary ?? 'Untitled minutes'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {meeting.action_item_count}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {meeting.status ? <StatusBadge status={meeting.status} /> : '—'}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/meetings/${meeting.meeting_id}/mom`}
                      className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors duration-150"
                    >
                      Review
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
