'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { CalendarIcon, PlusIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { ScheduleProposal } from '@/lib/types'

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

export default function SchedulePage() {
  const router = useRouter()
  const [proposals, setProposals] = useState<ScheduleProposal[]>([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchProposals = useCallback(async () => {
    setError(null)
    try {
      const data = await api.get<ScheduleProposal[]>('/schedule')
      setProposals(data)
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : 'Failed to load proposals',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchProposals()
  }, [fetchProposals])

  async function handleGenerate() {
    setGenerating(true)
    setError(null)
    try {
      const proposal = await api.post<ScheduleProposal>('/schedule/online', {})
      router.push(`/schedule/${proposal.id}`)
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : 'Failed to generate schedule',
      )
      setGenerating(false)
    }
  }

  return (
    <div className="px-6 py-8 max-w-[1200px]">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Schedule</h1>
          <p className="text-sm text-slate-500 mt-1">
            Propose conflict-free meeting slots for all team members.
          </p>
        </div>
        <button
          type="button"
          disabled={generating}
          onClick={handleGenerate}
          className="flex items-center gap-2 rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generating ? (
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
          ) : (
            <PlusIcon className="h-4 w-4" aria-hidden="true" />
          )}
          {generating ? 'Generating...' : 'New Proposal'}
        </button>
      </div>

      {error && (
        <p className="mb-4 text-sm text-red-600">{error}</p>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
        </div>
      ) : proposals.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <CalendarIcon className="h-12 w-12 text-slate-300 mb-4" />
          <p className="text-sm font-medium text-slate-900 mb-1">No proposals yet</p>
          <p className="text-xs text-slate-500">
            Click &quot;New Proposal&quot; to find available meeting slots.
          </p>
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-slate-200">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Created
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wide">
                  Slots
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
              {proposals.map((p) => (
                <tr key={p.id} className="hover:bg-slate-50 transition-colors duration-100">
                  <td className="px-4 py-3 text-sm text-slate-700">
                    {formatDate(p.created_at)}
                  </td>
                  <td className="px-4 py-3 text-sm text-slate-600">
                    {p.slots.length} slot{p.slots.length !== 1 ? 's' : ''}
                  </td>
                  <td className="px-4 py-3">
                    <StatusBadge status={p.status} />
                  </td>
                  <td className="px-4 py-3 text-right">
                    <Link
                      href={`/schedule/${p.id}`}
                      className="text-xs font-medium text-blue-600 hover:text-blue-800"
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
