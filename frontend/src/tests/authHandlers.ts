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
  )
}
