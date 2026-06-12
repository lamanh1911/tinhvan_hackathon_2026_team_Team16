import type { DRAFT_STATUS } from '@/lib/constants'

export type DraftStatus = (typeof DRAFT_STATUS)[keyof typeof DRAFT_STATUS]

export type MemberRole = 'Sales' | 'BrSE' | 'Admin'

export type MeetingMode = 'online' | 'offline'

export type EmailType = 'thank_you' | 'follow_up'

// --- API error shape (matches backend error format) ---
export interface ApiError {
  code: string
  message: string
  details?: Record<string, unknown>
}

export interface ApiErrorResponse {
  error: ApiError
}

// --- Domain types (mirror Pydantic response schemas) ---

export interface Customer {
  id: string
  name: string
  company: string
  email: string
  phone: string | null
  title: string | null
  address: string | null
  created_at: string
  updated_at: string
}

export interface FieldWithConfidence {
  value: string | null
  confidence: number | null
  flagged: boolean
}

export interface BusinessCard {
  id: string
  customer_id: string | null
  image_ref: string
  confidence: number | null
  language: string | null
  status: string
  fields?: Record<string, FieldWithConfidence>
  created_at: string
}

export interface CardFields {
  name: FieldWithConfidence
  company: FieldWithConfidence
  job_title: FieldWithConfidence
  email: FieldWithConfidence
  phone: FieldWithConfidence
  address: FieldWithConfidence
  website: FieldWithConfidence
}

export interface CardScanResponse {
  id: string
  status: string
  card_type: string
  fields: CardFields
  is_valid_card: boolean
  error_message: string | null
  created_at: string
}

export interface CardConfirmResponse {
  id: string
  customer_id: string
  status: string
}

export interface Meeting {
  id: string
  customer_id: string
  mode: MeetingMode
  start_time: string | null
  end_time: string | null
  location: string | null
  graph_event_id: string | null
  created_at: string
}

export interface ActionItem {
  id: string
  description: string
  owner: string | null
  deadline: string | null
}

export interface MeetingMinutes {
  id: string
  meeting_id: string
  summary: string | null
  language: string | null
  status: DraftStatus
  incomplete_warning: boolean
  action_items: ActionItem[]
  created_at: string
}

export interface MeetingListItem {
  meeting_id: string
  minutes_id: string | null
  status: DraftStatus | null
  summary: string | null
  incomplete_warning: boolean
  action_item_count: number
  created_at: string
}

export interface EmailDraft {
  id: string
  meeting_id: string
  type: EmailType
  subject: string | null
  body: string | null
  status: DraftStatus
  created_at: string
  updated_at: string
}

export interface Member {
  id: string
  name: string
  email: string
  role: MemberRole
}
