import { createContext } from 'react'

import type { AuthStatus, LoginPayload, User } from '../types/auth'

export type AuthContextValue = {
  user: User | null
  status: AuthStatus
  errorMessage: string | null
  login: (payload: LoginPayload) => Promise<void>
  logout: () => Promise<void>
  bootstrap: () => Promise<void>
}

export const AuthContext = createContext<AuthContextValue | null>(null)
