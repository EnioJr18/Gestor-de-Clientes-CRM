import { http, HttpResponse } from 'msw'

import type { User } from '../features/auth/types/auth'
import { server } from './server'

export const apiBaseUrl = 'http://localhost:8000/api/v1'
export const testUser: User = {
  id: 1,
  username: 'ana',
  first_name: 'Ana',
  last_name: 'Silva',
  email: 'ana@example.com',
}
const dashboardSummary = { period: { key: '30d', date_from: '2026-06-16', date_to: '2026-07-15' }, metrics: { total_leads: 0, created_today: 0, created_in_period: 0, converted_in_period: 0, conversion_rate: 0 }, by_status: [], by_priority: [], monthly_evolution: [], recent_leads: [], interaction_total: 0, interaction_by_type: [], leads_with_interaction: 0, leads_without_interaction: 0, interaction_monthly_evolution: [] }

export function mockUnauthenticatedBootstrap() {
  server.use(
    http.get(`${apiBaseUrl}/auth/csrf/`, () => HttpResponse.json({ csrfToken: 'csrf-test' })),
    http.post(`${apiBaseUrl}/auth/refresh/`, () =>
      HttpResponse.json(
        { status: 401, code: 'authentication_failed', message: 'Refresh token ausente.', errors: null },
        { status: 401 },
      ),
    ),
  )
}

export function mockAuthenticatedBootstrap() {
  server.use(
    http.get(`${apiBaseUrl}/auth/csrf/`, () => HttpResponse.json({ csrfToken: 'csrf-test' })),
    http.post(`${apiBaseUrl}/auth/refresh/`, () =>
      HttpResponse.json({ access: 'boot-access', token_type: 'Bearer', expires_in: 300 }),
    ),
    http.get(`${apiBaseUrl}/users/me/`, ({ request }) => {
      if (request.headers.get('authorization') !== 'Bearer boot-access') {
        return new HttpResponse(null, { status: 401 })
      }
      return HttpResponse.json(testUser)
    }),
    http.get(`${apiBaseUrl}/dashboard/summary/`, () => HttpResponse.json(dashboardSummary)),
  )
}
