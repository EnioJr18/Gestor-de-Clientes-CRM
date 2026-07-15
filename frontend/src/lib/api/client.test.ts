import { delay, http, HttpResponse } from 'msw'

import { apiBaseUrl } from '../../tests/authHandlers'
import { server } from '../../tests/server'
import { apiClient, setSessionExpiredHandler } from './client'
import { getAccessToken, setAccessToken } from './tokenStore'

describe('interceptors e refresh serializado', () => {
  it('faz um unico refresh para dois 401 e repete ambas as requisicoes', async () => {
    let refreshCalls = 0
    server.use(
      http.get(`${apiBaseUrl}/auth/csrf/`, () => HttpResponse.json({ csrfToken: 'csrf' })),
      http.post(`${apiBaseUrl}/auth/refresh/`, async () => {
        refreshCalls += 1
        await delay(20)
        return HttpResponse.json({ access: 'new-access', token_type: 'Bearer', expires_in: 300 })
      }),
      http.get(`${apiBaseUrl}/resource/:id`, ({ request, params }) => {
        if (request.headers.get('authorization') !== 'Bearer new-access') {
          return new HttpResponse(null, { status: 401 })
        }
        return HttpResponse.json({ id: params.id })
      }),
    )
    setAccessToken('expired-access')

    const [first, second] = await Promise.all([
      apiClient.get('/resource/one'),
      apiClient.get('/resource/two'),
    ])

    expect(refreshCalls).toBe(1)
    expect(first.data).toEqual({ id: 'one' })
    expect(second.data).toEqual({ id: 'two' })
    expect(getAccessToken()).toBe('new-access')
  })

  it('encerra a sessao quando o refresh falha sem entrar em loop', async () => {
    let protectedCalls = 0
    let refreshCalls = 0
    const expired = vi.fn()
    setSessionExpiredHandler(expired)
    server.use(
      http.get(`${apiBaseUrl}/auth/csrf/`, () => HttpResponse.json({ csrfToken: 'csrf' })),
      http.post(`${apiBaseUrl}/auth/refresh/`, () => {
        refreshCalls += 1
        return new HttpResponse(null, { status: 401 })
      }),
      http.get(`${apiBaseUrl}/protected`, () => {
        protectedCalls += 1
        return new HttpResponse(null, { status: 401 })
      }),
    )
    setAccessToken('expired')

    await expect(apiClient.get('/protected')).rejects.toBeDefined()
    expect(refreshCalls).toBe(1)
    expect(protectedCalls).toBe(1)
    expect(expired).toHaveBeenCalledOnce()
    expect(getAccessToken()).toBeNull()
  })

  it('nao sobrescreve Authorization explicito', async () => {
    let receivedHeader: string | null = null
    server.use(
      http.get(`${apiBaseUrl}/explicit`, ({ request }) => {
        receivedHeader = request.headers.get('authorization')
        return HttpResponse.json({ ok: true })
      }),
    )
    setAccessToken('memory-token')
    await apiClient.get('/explicit', { headers: { Authorization: 'Custom credential' } })
    expect(receivedHeader).toBe('Custom credential')
  })

  it('nao envia Bearer aos endpoints de autenticacao', async () => {
    let receivedHeader: string | null = null
    server.use(
      http.get(`${apiBaseUrl}/auth/csrf/`, ({ request }) => {
        receivedHeader = request.headers.get('authorization')
        return HttpResponse.json({ csrfToken: 'csrf' })
      }),
    )
    setAccessToken('memory-token')
    await apiClient.get('/auth/csrf/')
    expect(receivedHeader).toBeNull()
  })
})
