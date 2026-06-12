'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import {
  ArrowLeftIcon,
  ClipboardDocumentIcon,
  CheckIcon,
} from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import type { EmailDraft } from '@/lib/types'

export default function EmailDetailPage() {
  const params = useParams()
  const emailId = params.id as string

  const [email, setEmail] = useState<EmailDraft | null>(null)
  const [subject, setSubject] = useState('')
  const [bodyText, setBodyText] = useState('')
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [actionError, setActionError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [copied, setCopied] = useState(false)

  const applyEmail = useCallback((data: EmailDraft) => {
    setEmail(data)
    setSubject(data.subject ?? '')
    setBodyText(data.body ?? '')
  }, [])

  const fetchEmail = useCallback(async () => {
    setFetchError(null)
    try {
      const data = await api.get<EmailDraft>(`/emails/${emailId}`)
      applyEmail(data)
    } catch (err) {
      setFetchError(
        err instanceof ApiRequestError ? err.message : 'Failed to load email',
      )
    } finally {
      setLoading(false)
    }
  }, [emailId, applyEmail])

  useEffect(() => {
    fetchEmail()
  }, [fetchEmail])

  const isSent = email?.status === 'sent'

  async function handleSave() {
    setBusy(true)
    setActionError(null)
    try {
      const updated = await api.patch<EmailDraft>(`/emails/${emailId}`, {
        subject,
        body: bodyText,
      })
      applyEmail(updated)
    } catch (err) {
      setActionError(err instanceof ApiRequestError ? err.message : 'Save failed')
    } finally {
      setBusy(false)
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(bodyText)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setActionError('Could not copy to clipboard')
    }
  }

  async function handleMarkSent() {
    setBusy(true)
    setActionError(null)
    try {
      const updated = await api.post<EmailDraft>(`/emails/${emailId}/mark-sent`, {})
      applyEmail(updated)
    } catch (err) {
      setActionError(err instanceof ApiRequestError ? err.message : 'Action failed')
    } finally {
      setBusy(false)
    }
  }

  if (loading) {
    return (
      <div className="px-6 py-8 flex items-center justify-center min-h-[200px]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
      </div>
    )
  }

  if (fetchError || !email) {
    return (
      <div className="px-6 py-8">
        <p className="text-sm text-red-600 mb-4">{fetchError ?? 'Email not found'}</p>
        <Link
          href="/emails"
          className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 transition-colors duration-150"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          Back to emails
        </Link>
      </div>
    )
  }

  const inputBase =
    'block w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none ' +
    'focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors duration-150 ' +
    'disabled:bg-slate-100 disabled:text-slate-500'

  return (
    <div className="px-6 py-8 max-w-3xl">
      <div className="mb-6 flex items-center gap-3">
        <Link
          href="/emails"
          className="text-slate-400 hover:text-slate-700 transition-colors duration-150"
          aria-label="Back to emails"
        >
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold text-slate-900">Follow-up Email</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Review the draft, then copy the body to send it yourself.
          </p>
        </div>
        <StatusBadge status={email.status} />
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-4 space-y-4">
        <div className="space-y-1">
          <label htmlFor="email-subject" className="block text-sm font-medium text-slate-700">
            Subject
          </label>
          <input
            id="email-subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
            disabled={isSent}
            placeholder="Email subject"
            className={inputBase}
          />
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <label htmlFor="email-body" className="block text-sm font-medium text-slate-700">
              Body
            </label>
            <button
              type="button"
              onClick={handleCopy}
              className="inline-flex items-center gap-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 transition-colors duration-150"
            >
              {copied ? (
                <>
                  <CheckIcon className="h-4 w-4" />
                  Copied
                </>
              ) : (
                <>
                  <ClipboardDocumentIcon className="h-4 w-4" />
                  Copy body
                </>
              )}
            </button>
          </div>
          <textarea
            id="email-body"
            value={bodyText}
            onChange={(e) => setBodyText(e.target.value)}
            disabled={isSent}
            rows={16}
            className={`${inputBase} resize-none`}
          />
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 space-y-4">
        {actionError && <p className="text-sm text-red-600">{actionError}</p>}

        {isSent ? (
          <p className="text-sm text-slate-600 bg-slate-100 border border-slate-200 rounded-md px-3 py-2">
            This follow-up is marked as sent and is now read-only.
          </p>
        ) : (
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleSave}
              disabled={busy}
              className="bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Save changes
            </button>
            <button
              type="button"
              onClick={handleMarkSent}
              disabled={busy}
              className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Mark as sent
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
