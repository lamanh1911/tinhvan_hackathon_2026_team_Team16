'use client'

import { useRouter } from 'next/navigation'
import { CardUpload } from '@/components/cards/CardUpload'
import type { CardScanResponse } from '@/lib/types'

export default function CardsPage() {
  const router = useRouter()

  function handleScanComplete(card: CardScanResponse) {
    console.log('[STEP 2] setState — card received from scan:', JSON.stringify(card, null, 2))
    console.log('[STEP 2] fields keys:', Object.keys(card.fields))
    console.log('[STEP 2] navigating to /cards/' + card.id)
    router.push(`/cards/${card.id}`)
  }

  return (
    <div className="px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Card Scan</h1>
        <p className="text-sm text-slate-500 mt-1">
          Upload a business card image to extract and verify contact information.
        </p>
      </div>
      <CardUpload onScanComplete={handleScanComplete} />
    </div>
  )
}
