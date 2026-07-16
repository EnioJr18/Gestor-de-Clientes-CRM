import '@testing-library/jest-dom/vitest'
import { createElement } from 'react'
import { cleanup } from '@testing-library/react'
import { afterAll, afterEach, beforeAll, vi } from 'vitest'

import { clearCsrfToken } from '../lib/api/csrf'
import { setSessionExpiredHandler } from '../lib/api/client'
import { clearAccessToken } from '../lib/api/tokenStore'
import { server } from './server'

vi.mock('react-chartjs-2', () => ({ Bar: () => createElement('div', { 'aria-label': 'Grafico de evolucao mensal' }), Doughnut: () => createElement('div', { 'aria-label': 'Grafico de leads por status' }) }))

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
