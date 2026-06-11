'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  CalendarIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  IdentificationIcon,
} from '@heroicons/react/24/outline'
import { ROUTES } from '@/lib/constants'

const NAV_ITEMS = [
  { label: 'Card Scan',  href: ROUTES.CARDS,    icon: IdentificationIcon },
  { label: 'Emails',     href: ROUTES.EMAILS,   icon: EnvelopeIcon },
  { label: 'Schedule',   href: ROUTES.SCHEDULE, icon: CalendarIcon },
  { label: 'Meetings',   href: ROUTES.MEETINGS, icon: DocumentTextIcon },
] as const

export function Sidebar() {
  const pathname = usePathname()

  return (
    <nav className="w-64 shrink-0 bg-white border-r border-slate-200 h-full py-4">
      <ul className="space-y-1 px-2">
        {NAV_ITEMS.map(({ label, href, icon: Icon }) => {
          const active = pathname === href || pathname.startsWith(`${href}/`)
          return (
            <li key={href}>
              <Link
                href={href}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors duration-150 ${
                  active
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`}
              >
                <Icon className="h-5 w-5 shrink-0" aria-hidden="true" />
                {label}
              </Link>
            </li>
          )
        })}
      </ul>
    </nav>
  )
}
