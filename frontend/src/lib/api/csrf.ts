import { csrfResponseSchema } from '../../features/auth/types/auth'
import { publicClient } from './transport'

let csrfToken: string | null = null
let csrfPromise: Promise<string> | null = null

export async function ensureCsrfToken(force = false): Promise<string> {
  if (!force && csrfToken) return csrfToken
  if (csrfPromise) return csrfPromise

  csrfPromise = publicClient
    .get('/auth/csrf/')
    .then((response) => csrfResponseSchema.parse(response.data).csrfToken)
    .then((token) => {
      csrfToken = token
      return token
    })
    .finally(() => {
      csrfPromise = null
    })

  return csrfPromise
}

export function clearCsrfToken(): void {
  csrfToken = null
  csrfPromise = null
}
