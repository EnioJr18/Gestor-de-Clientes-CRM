import { refreshResponseSchema } from '../../features/auth/types/auth'
import { clearAccessToken, setAccessToken } from './tokenStore'
import { ensureCsrfToken } from './csrf'
import { publicClient } from './transport'

let refreshPromise: Promise<string> | null = null

async function executeRefresh(): Promise<string> {
  const csrfToken = await ensureCsrfToken()
  const response = await publicClient.post(
    '/auth/refresh/',
    {},
    { headers: { 'X-CSRFToken': csrfToken } },
  )
  const parsed = refreshResponseSchema.parse(response.data)
  setAccessToken(parsed.access)
  return parsed.access
}

export function refreshAccessToken(): Promise<string> {
  if (!refreshPromise) {
    refreshPromise = executeRefresh()
      .catch((error: unknown) => {
        clearAccessToken()
        throw error
      })
      .finally(() => {
        refreshPromise = null
      })
  }
  return refreshPromise
}
