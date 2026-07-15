import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach, beforeAll } from 'vitest'

import { clearCsrfToken } from '../lib/api/csrf'
import { setSessionExpiredHandler } from '../lib/api/client'
import { clearAccessToken } from '../lib/api/tokenStore'
import { server } from './server'

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }))
afterEach(() => {
  cleanup()
  server.resetHandlers()
  clearAccessToken()
  clearCsrfToken()
  setSessionExpiredHandler(null)
  localStorage.clear()
  sessionStorage.clear()
})
afterAll(() => server.close())
