export const DRAFT_STATUS = {
  DRAFT: 'draft',
  IN_REVIEW: 'in_review',
  APPROVED: 'approved',
  SENT: 'sent',
  REJECTED: 'rejected',
} as const

export const ROUTES = {
  HOME: '/',
  CARDS: '/cards',
  EMAILS: '/emails',
  SCHEDULE: '/schedule',
  MEETINGS: '/meetings',
} as const

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000'
