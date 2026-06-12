'use client'

import { useCallback, useEffect, useState } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { SlotList } from '@/components/schedule/SlotList'
import type { ScheduleProposal } from '@/lib/types'

export default function ScheduleProposalPage() {
  const { id } = useParams<{ id: string }>()
  const router = useRouter()
  const [proposal, setProposal] = useState<ScheduleProposal | null>(null)
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchProposal = useCallback(async () => {
    setError(null)
    try {
      const data = await api.get<ScheduleProposal>(`/schedule/${id}`)
      setProposal(data)
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : 'Failed to load proposal',
      )
    } finally {
      setLoading(false)
    }
  }, [id])

  useEffect(() => {
    fetchProposal()
  }, [fetchProposal])

  async function handleApprove(slotIndex: number) {
    if (!proposal) return
    setApproving(true)
    setError(null)
    try {
      const updated = await api.post<ScheduleProposal>(
        `/schedule/${proposal.id}/approve`,
        { slot_index: slotIndex },
      )
      setProposal(updated)
    } catch (err) {
      setError(
        err instanceof ApiRequestError ? err.message : 'Failed to approve slot',
      )
    } finally {
      setApproving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-24">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
      </div>
    )
  }

  if (!proposal) {
    return (
      <div className="px-6 py-8">
        <p className="text-sm text-red-600">{error ?? 'Proposal not found.'}</p>
      </div>
    )
  }

  const isApproved = proposal.status === 'approved'

  return (
    <div className="px-6 py-8 max-w-[800px]">
      <button
        type="button"
        onClick={() => router.push('/schedule')}
        className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-slate-800 mb-6 transition-colors duration-150"
      >
        <ArrowLeftIcon className="h-4 w-4" aria-hidden="true" />
        Back to Schedule
      </button>

      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Schedule Proposal</h1>
          <p className="text-sm text-slate-500 mt-1">
            {proposal.slots.length} conflict-free slot{proposal.slots.length !== 1 ? 's' : ''} found
          </p>
        </div>
        <StatusBadge status={proposal.status} />
      </div>

      {error && (
        <p className="mb-4 text-sm text-red-600">{error}</p>
      )}

      {isApproved && proposal.approved_slot_index !== null && (
        <div className="mb-6 rounded-lg border border-green-300 bg-green-50 px-4 py-3">
          <p className="text-sm font-medium text-green-800">
            Slot {proposal.approved_slot_index + 1} has been selected. No further changes can be made.
          </p>
        </div>
      )}

      {proposal.slots.length === 0 ? (
        <div className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-6 text-center">
          <p className="text-sm font-medium text-amber-800">No available slots found</p>
          <p className="text-xs text-amber-700 mt-1">
            All team members are busy for the search window. Try a later start date.
          </p>
        </div>
      ) : (
        <SlotList
          slots={proposal.slots}
          approvedIndex={proposal.approved_slot_index}
          onApprove={!isApproved ? handleApprove : undefined}
          disabled={approving}
        />
      )}
    </div>
  )
}
