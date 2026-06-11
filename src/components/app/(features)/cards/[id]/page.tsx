'use client'

import { useCallback, useEffect, useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'
import { ArrowLeftIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import { CardFieldEditor } from '@/components/cards/CardFieldEditor'
import { CardActions } from '@/components/cards/CardActions'
import type { CardFields, CardScanResponse } from '@/lib/types'

const FIELD_LABELS: Record<keyof CardFields, string> = {
  name: 'Full Name',
  company: 'Company',
  title: 'Job Title',
  email: 'Email',
  phone: 'Phone',
  address: 'Address',
}

const REQUIRED_FIELDS: Array<keyof CardFields> = ['name', 'company', 'email']
const FIELD_ORDER: Array<keyof CardFields> = [
  'name',
  'company',
  'title',
  'email',
  'phone',
  'address',
]

export default function CardReviewPage() {
  const params = useParams()
  const cardId = params.id as string

  const [card, setCard] = useState<CardScanResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState<string | null>(null)
  const [confirming, setConfirming] = useState(false)
  const [confirmError, setConfirmError] = useState<string | null>(null)

  const fetchCard = useCallback(async () => {
    setFetchError(null)
    try {
      const data = await api.get<CardScanResponse>(`/cards/${cardId}`)
      setCard(data)
    } catch (err) {
      setFetchError(
        err instanceof ApiRequestError ? err.message : 'Failed to load card',
      )
    } finally {
      setLoading(false)
    }
  }, [cardId])

  useEffect(() => {
    fetchCard()
  }, [fetchCard])

  async function handleFieldSave(fieldName: string, value: string) {
    const updated = await api.patch<CardScanResponse>(`/cards/${cardId}`, {
      [fieldName]: value,
    })
    setCard(updated)
  }

  async function handleConfirm() {
    setConfirming(true)
    setConfirmError(null)
    try {
      await api.post(`/cards/${cardId}/confirm`, {})
      const updated = await api.get<CardScanResponse>(`/cards/${cardId}`)
      setCard(updated)
    } catch (err) {
      setConfirmError(
        err instanceof ApiRequestError ? err.message : 'Confirm failed',
      )
    } finally {
      setConfirming(false)
    }
  }

  if (loading) {
    return (
      <div className="px-6 py-8 flex items-center justify-center min-h-[200px]">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
      </div>
    )
  }

  if (fetchError || !card) {
    return (
      <div className="px-6 py-8">
        <p className="text-sm text-red-600 mb-4">{fetchError ?? 'Card not found'}</p>
        <Link
          href="/cards"
          className="inline-flex items-center gap-1.5 text-sm text-blue-600 hover:text-blue-700 transition-colors duration-150"
        >
          <ArrowLeftIcon className="h-4 w-4" />
          Back to upload
        </Link>
      </div>
    )
  }

  return (
    <div className="px-6 py-8 max-w-2xl">
      <div className="mb-6 flex items-center gap-3">
        <Link
          href="/cards"
          className="text-slate-400 hover:text-slate-700 transition-colors duration-150"
          aria-label="Back to card upload"
        >
          <ArrowLeftIcon className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Review Card</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Verify and correct extracted fields before confirming.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6 mb-4">
        <h2 className="text-lg font-medium text-slate-900 mb-4">
          Extracted Fields
        </h2>
        <div className="space-y-3">
          {FIELD_ORDER.map((fieldName) => (
            <CardFieldEditor
              key={fieldName}
              fieldName={fieldName}
              label={FIELD_LABELS[fieldName]}
              field={card.fields[fieldName]}
              required={REQUIRED_FIELDS.includes(fieldName)}
              onSave={handleFieldSave}
            />
          ))}
        </div>
      </div>

      <div className="bg-white rounded-lg border border-slate-200 shadow-sm p-6">
        {confirmError && (
          <p className="mb-3 text-sm text-red-600">{confirmError}</p>
        )}
        <CardActions
          card={card}
          confirming={confirming}
          onConfirm={handleConfirm}
        />
      </div>
    </div>
  )
}
