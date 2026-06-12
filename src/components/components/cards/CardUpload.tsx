'use client'

import { useCallback, useRef, useState } from 'react'
import { CloudArrowUpIcon, ExclamationCircleIcon, XMarkIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import type { CardScanResponse } from '@/lib/types'

interface CardUploadProps {
  onScanComplete: (card: CardScanResponse) => void
}

const ERROR_TITLES: Record<string, string> = {
  WRONG_CARD_TYPE: 'Wrong card type',
  INVALID_CARD_TYPE: 'Not a business card',
  POOR_QUALITY: 'Image quality too low',
}

export function CardUpload({ onScanComplete }: CardUploadProps) {
  const [dragging, setDragging] = useState(false)
  const [scanning, setScanning] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [errorCode, setErrorCode] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  function clearError() {
    setError(null)
    setErrorCode(null)
  }

  const handleFile = useCallback(
    async (file: File) => {
      if (!file.type.startsWith('image/')) {
        setError('Please upload an image file (JPG, PNG, etc.)')
        setErrorCode(null)
        return
      }
      clearError()
      setScanning(true)
      try {
        const form = new FormData()
        form.append('file', file)
        const card = await api.postForm<CardScanResponse>('/cards/scan', form)
        onScanComplete(card)
      } catch (err) {
        if (err instanceof ApiRequestError) {
          setErrorCode(err.code)
          setError(err.message)
        } else {
          setErrorCode(null)
          setError('Scan failed. Please try again.')
        }
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
    <div className="max-w-lg space-y-4">
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
        aria-label="Upload business card image"
        className="hidden"
        onChange={onInputChange}
        disabled={scanning}
      />

      {error && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-start gap-3">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm font-semibold text-red-800">
                {ERROR_TITLES[errorCode ?? ''] ?? 'Upload failed'}
              </p>
              <p className="text-sm text-red-700 mt-0.5">{error}</p>
              {(errorCode === 'WRONG_CARD_TYPE' || errorCode === 'INVALID_CARD_TYPE') && (
                <p className="text-xs text-red-600 mt-2">
                  Please upload a business card (name card / visiting card) only.
                </p>
              )}
              {errorCode === 'POOR_QUALITY' && (
                <p className="text-xs text-red-600 mt-2">
                  Please retake the photo in better lighting, or upload a clearer image.
                </p>
              )}
            </div>
            <button
              type="button"
              aria-label="Dismiss error"
              onClick={clearError}
              className="shrink-0 text-red-400 hover:text-red-600 transition-colors duration-150"
            >
              <XMarkIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
