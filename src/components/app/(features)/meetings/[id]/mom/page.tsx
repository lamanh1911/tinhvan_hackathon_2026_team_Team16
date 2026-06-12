'use client'

import { useCallback, useEffect, useMemo, useState } from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { ArrowLeftIcon, EnvelopeIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { MOMSummary } from '@/components/meetings/MOMSummary'
import { ActionItemList } from '@/components/meetings/ActionItemList'
import { MOMActions } from '@/components/meetings/MOMActions'
import { MissingFieldWarning } from '@/components/meetings/MissingFieldWarning'
import type { ActionItemDraft } from '@/components/meetings/ActionItemRow'
import type { EmailDraft, MeetingMinutes } from '@/lib/types'

function toDrafts(mom: MeetingMinutes): ActionItemDraft[] {
  return mom.action_items.map((item) => ({
    id: item.id,
    description: item.description,
    owner: item.owner ?? '',
    deadline: item.deadline ?? '',
  }))
}

export default function MomReviewPage() {
  const params = useParams()
  const router = useRouter()
  const meetingId = params.id as string

  const [mom, setMom] = useState<MeetingMinutes | null>(null)
  const [summary, setSummary] = useState('')
  const [items, setItems] = useState<ActionItemDraft[]>([])
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [approving, setApproving] = useState(false)
  const [generating, setGenerating] = useState(false)

  const applyMom = useCallback((data: MeetingMinutes) => {
    setMom(data)
    setSummary(data.summary ?? '')
    setItems(toDrafts(data))
  }, [])

  const fetchMom = useCallback(async () => {
    setFetchError(null)
    try {
      const data = await api.get<MeetingMinutes>(`/meetings/${meetingId}/mom`)
      applyMom(data)
    } catch (err) {
      setFetchError(
        err instanceof ApiRequestError ? err.message : 'Failed to load minutes',
      )
    } finally {
      setLoading(false)
    }
  }, [meetingId, applyMom])

  useEffect(() => {
    fetchMom()
  }, [fetchMom])

  const isApproved = mom?.status === 'approved'

  const validationMessages = useMemo(() => {
    const messages: string[] = []
    if (summary.trim() === '') messages.push('Add a discussion summary')
    if (items.length === 0) messages.push('Add at least one action item')
    items.forEach((item, index) => {
      const missing: string[] = []
      if (item.description.trim() === '') missing.push('description')
      if (item.owner.trim() === '') missing.push('owner')
      if (item.deadline.trim() === '') missing.push('deadline')
      if (missing.length > 0) {
        messages.push(`Action item ${index + 1}: ${missing.join(', ')}`)
      }
    })
    return messages
  }, [summary, items])

  const canApprove = validationMessages.length === 0

  function buildPayload() {
    return {
      summary,
      action_items: items.map((item) => ({
        description: item.description,
        owner: item.owner.trim() === '' ? null : item.owner,
        deadline: item.deadline.trim() === '' ? null : item.deadline,
      })),
    }
  }

  async function handleSave() {
    setSaving(true)
    setActionError(null)
    try {
      const updated = await api.patch<MeetingMinutes>(
        `/meetings/${meetingId}/mom`,
        buildPayload(),
      )
      applyMom(updated)
    } catch (err) {
      setActionError(err instanceof ApiRequestError ? err.message : 'Save failed')
    } finally {
      setSaving(false)
    }
  }

  async function handleApprove() {
    setApproving(true)
    setActionError(null)
    try {
      await api.patch<MeetingMinutes>(`/meetings/${meetingId}/mom`, buildPayload())
      const approved = await api.post<MeetingMinutes>(
        `/meetings/${meetingId}/mom/approve`,
        {},
      )
      applyMom(approved)
    } catch (err) {
      setActionError(err instanceof ApiRequestError ? err.message : 'Approve failed')
    } finally {
      setApproving(false)
    }
  }

  async function handleGenerateFollowUp() {
    setGenerating(true)
    setActionError(null)
    try {
      const email = await api.post<EmailDraft>('/emails/follow-up', {
        meeting_id: meetingId,
      })
      router.push(`/emails/${email.id}`)
    } catch (err) {
      setActionError(
        err instanceof ApiRequestError ? err.message : 'Could not generate email',
      )
      setGenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="px-6 py-8 flex items-center justify-center min-h-[200px]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
      </div>
    )
  }

  if (fetchError || !mom) {
    return (
      <div className="px-6 py-8">
        <p className="text-sm text-red-600 mb-4">{fetchError ?? 'Minutes not found'}</p>
        <Link
          href="/meetings"
          className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 transition-colors duration-150"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          Back to meetings
        </Link>
      </div>
    )
  }

  return (
    <div className="px-6 py-8 max-w-3xl">
      <div className="mb-6 flex items-center gap-3">
        <Link
          href="/meetings"
          className="text-slate-400 hover:text-slate-700 transition-colors duration-150"
          aria-label="Back to meetings"
        >
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-slate-900">Meeting Minutes</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Review and edit the generated minutes before approving.
          </p>
        </div>
        <StatusBadge status={mom.status} />
      </div>

      {mom.incomplete_warning && (
        <div
          role="alert"
          className="mb-4 flex items-start gap-3 bg-amber-50 border border-amber-200 text-amber-800 rounded-lg px-4 py-3 text-sm"
        >
          <span>
            The transcript may be incomplete. Please verify the summary and action
            items carefully.
          </span>
        </div>
      )}

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-4">
        <MOMSummary value={summary} onChange={setSummary} readOnly={isApproved} />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-4">
        <ActionItemList items={items} onChange={setItems} readOnly={isApproved} />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 space-y-4">
        {actionError && <p className="text-sm text-red-600">{actionError}</p>}

        {!isApproved && <MissingFieldWarning messages={validationMessages} />}

        <MOMActions
          isApproved={!!isApproved}
          canApprove={canApprove}
          saving={saving}
          approving={approving}
          onSave={handleSave}
          onApprove={handleApprove}
        />

        {isApproved && (
          <button
            type="button"
            onClick={handleGenerateFollowUp}
            disabled={generating}
            className="inline-flex items-center gap-2 bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <EnvelopeIcon className="h-4 w-4" />
            {generating ? 'Generating...' : 'Generate follow-up email'}
          </button>
        )}
      </div>
    </div>
  )
}
