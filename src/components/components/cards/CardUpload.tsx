'use client'

import { useCallback, useRef, useState } from 'react'
import { CloudArrowUpIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import type { CardScanResponse } from '@/lib/types'

interface CardUploadProps {
  onScanComplete: (card: CardScanResponse) => void
}

export function CardUpload({ onScanComplete }: CardUploadProps) {
  const [dragging, setDragging] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file (JPG, PNG, etc.)')
        return
      }
      setError(null)
      setScanning(true)
      try {
        const form = new FormData()
        form.append('file', file)
        const card = await api.postForm<CardScanResponse>('/cards/scan', form)
        console.log('[STEP 1] scan API response:', JSON.stringify(card, null, 2))
        onScanComplete(card)
      } catch (err) {
        setError(
          err instanceof ApiRequestError
            ? err.message
            : 'Scan failed. Please try again.',
        )
      } finally {
        setScanning(false)
      }
    },
    [onScanComplete],
  )

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragging(false)
      const file = e.dataTransfer.files[0]
      if (file) handleFile(file)
    },
    [handleFile],
  )

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) handleFile(file)
    e.target.value = ''
  }

  return (
    <div className="max-w-lg">
      <div
        onDragOver={(e) => {
          e.preventDefault()
          if (!scanning) setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !scanning && fileInputRef.current?.click()}
        className={[
          'flex flex-col items-center justify-center gap-4',
          'border-2 border-dashed rounded-lg p-16 cursor-pointer',
          'transition-colors duration-150',
          dragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-slate-300 bg-white hover:border-blue-400 hover:bg-slate-50',
          scanning ? 'cursor-not-allowed opacity-60 pointer-events-none' : '',
        ]
          .join(' ')
          .trim()}
      >
        {scanning ? (
          <>
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
            <p className="text-sm text-slate-600 font-medium">Scanning card...</p>
          </>
        ) : (
          <>
            <CloudArrowUpIcon className="h-12 w-12 text-slate-400" />
            <div className="text-center">
              <p className="text-sm font-medium text-slate-700">
                Drop your business card image here
              </p>
              <p className="text-xs text-slate-500 mt-1">
                or click to browse — JPG, PNG supported
              </p>
            </div>
          </>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={onInputChange}
        disabled={scanning}
      />

      {error && (
        <p className="mt-3 text-sm text-red-600 text-center">{error}</p>
      )}
    </div>
  )
}
