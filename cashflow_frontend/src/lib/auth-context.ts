import { createContext, useContext } from 'react'
import type { User } from '@/lib/api'

export interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isLoggingOut: boolean
  isAuthenticated: boolean
  refreshUser: () => Promise<User | null>
  logout: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used inside AuthProvider')
  }
  return context
}
