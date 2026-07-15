import { useQueryClient } from '@tanstack/react-query'
import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'

import { setSessionExpiredHandler } from '../../../lib/api/client'
import { ensureCsrfToken } from '../../../lib/api/csrf'
import { refreshAccessToken } from '../../../lib/api/refresh'
import { clearAccessToken, setAccessToken } from '../../../lib/api/tokenStore'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { currentUserRequest, loginRequest, logoutRequest } from '../api/authApi'
import type { AuthStatus, LoginPayload, User } from '../types/auth'
import { AuthContext } from './AuthContext'

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<User | null>(null)
  const [status, setStatus] = useState<AuthStatus>('idle')
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const bootstrapStarted = useRef(false)

  const expireSession = useCallback(() => {
    clearAccessToken()
    setUser(null)
    setStatus('unauthenticated')
    setErrorMessage('Sua sessao expirou. Entre novamente.')
    queryClient.removeQueries({ predicate: (query) => query.meta?.private === true })
  }, [queryClient])

  const bootstrap = useCallback(async () => {
    setStatus('loading')
    setErrorMessage(null)
    try {
      await ensureCsrfToken()
      await refreshAccessToken()
      setUser(await currentUserRequest())
      setStatus('authenticated')
    } catch (error: unknown) {
      clearAccessToken()
      setUser(null)
      const normalized = normalizeApiError(error)
      if ([401, 403].includes(normalized.status)) {
        setStatus('unauthenticated')
        setErrorMessage(null)
      } else {
        setStatus('error')
        setErrorMessage(normalized.message)
      }
    }
  }, [])

  useEffect(() => {
    setSessionExpiredHandler(expireSession)
    if (!bootstrapStarted.current) {
      bootstrapStarted.current = true
      void bootstrap()
    }
    return () => setSessionExpiredHandler(null)
  }, [bootstrap, expireSession])

  const login = useCallback(async (payload: LoginPayload) => {
    const response = await loginRequest(payload)
    setAccessToken(response.access)
    setUser(response.user)
    setStatus('authenticated')
    setErrorMessage(null)
  }, [])

  const logout = useCallback(async () => {
    try {
      await logoutRequest()
    } catch {
      // O estado local deve ser encerrado mesmo se o refresh ja estiver revogado.
    } finally {
      clearAccessToken()
      setUser(null)
      setStatus('unauthenticated')
      setErrorMessage(null)
      queryClient.removeQueries({ predicate: (query) => query.meta?.private === true })
    }
  }, [queryClient])

  return (
    <AuthContext.Provider value={{ user, status, errorMessage, login, logout, bootstrap }}>
      {children}
    </AuthContext.Provider>
  )
}
