'use client'

import { useAuth } from '@/lib/auth'

export function Header() {
  const { user } = useAuth()

  const initials = user.name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .slice(0, 2)
    .toUpperCase()

  return (
    <header className="h-[60px] shrink-0 bg-white border-b border-slate-200 flex items-center px-6 gap-4">
      <span className="text-lg font-semibold text-slate-900 tracking-tight">
        Relay
      </span>
      <div className="flex-1" />
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-500">{user.name}</span>
        <div
          className="h-8 w-8 rounded-full bg-blue-600 flex items-center justify-center text-white text-xs font-semibold shrink-0"
          aria-label={`Logged in as ${user.name}`}
        >
          {initials}
        </div>
      </div>
    </header>
  )
}
