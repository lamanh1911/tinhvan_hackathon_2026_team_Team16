'use client'

import { useCallback, useRef, useState } from 'react'
import { DocumentArrowUpIcon } from '@heroicons/react/24/outline'
import { api, ApiRequestError } from '@/lib/api-client'
import type { MeetingMinutes } from '@/lib/types'

interface TranscriptUploadProps {
  onMomCreated: (mom: MeetingMinutes) => void
}

const ALLOWED_EXTENSIONS = ['.txt', '.docx']

function hasAllowedExtension(name: string): boolean {
  const lower = name.toLowerCase()
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext))
}

export function TranscriptUpload({ onMomCreated }: TranscriptUploadProps) {
  const [dragging, setDragging] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFile = useCallback(
    async (file: File) => {
      if (!hasAllowedExtension(file.name)) {
        setError('Please upload a .txt or .docx transcript file')
        return
      }
      setError(null)
      setProcessing(true)
      try {
        const form = new FormData()
        form.append('file', file)
        const mom = await api.postForm<MeetingMinutes>('/meetings/mom', form)
        onMomCreated(mom)
      } catch (err) {
        setError(
          err instanceof ApiRequestError
            ? err.message
            : 'Could not generate minutes. Please try again.',
        )
      } finally {
        setProcessing(false)
      }
    },
    [onMomCreated],
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
          if (!processing) setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        onClick={() => !processing && fileInputRef.current?.click()}
        className={[
          'flex flex-col items-center justify-center gap-4',
          'border-2 border-dashed rounded-lg p-16 cursor-pointer',
          'transition-colors duration-150',
          dragging
            ? 'border-blue-500 bg-blue-50'
            : 'border-slate-300 bg-white hover:border-blue-400 hover:bg-slate-50',
          processing ? 'cursor-not-allowed opacity-60 pointer-events-none' : '',
        ]
          .join(' ')
          .trim()}
      >
        {processing ? (
          <>
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
            <p className="text-sm text-slate-600 font-medium">
              Generating minutes...
            </p>
          </>
        ) : (
          <>
            <DocumentArrowUpIcon className="h-12 w-12 text-slate-400" />
            <div className="text-center">
              <p className="text-sm font-medium text-slate-700">
                Drop your meeting transcript here
              </p>
              <p className="text-xs text-slate-500 mt-1">
                or click to browse — TXT, DOCX supported
              </p>
            </div>
          </>
        )}
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".txt,.docx"
        className="hidden"
        onChange={onInputChange}
        disabled={processing}
      />

      {error && <p className="mt-3 text-sm text-red-600 text-center">{error}</p>}
    </div>
  )
}
