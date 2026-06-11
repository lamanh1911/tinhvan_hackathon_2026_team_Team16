'use client'

import { createContext, useContext } from 'react'
import type { Member } from '@/lib/types'

type MockUser = Pick<Member, 'id' | 'name' | 'email' | 'role'>

const MOCK_USER: MockUser = {
  id: 'mock-user-001',
  name: 'Dev User',
  email: 'dev@relay.local',
  role: 'Sales',
}

interface AuthContextValue {
  user: MockUser
}

const AuthContext = createContext<AuthContextValue>({ user: MOCK_USER })

export function AuthProvider({ children }: { children: React.ReactNode }) {
  return (
    <AuthContext.Provider value={{ user: MOCK_USER }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  return useContext(AuthContext)
}
