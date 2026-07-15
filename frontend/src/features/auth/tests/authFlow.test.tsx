import { delay, http, HttpResponse } from 'msw'
import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { getAccessToken } from '../../../lib/api/tokenStore'
import { apiBaseUrl, mockAuthenticatedBootstrap, mockUnauthenticatedBootstrap, testUser } from '../../../tests/authHandlers'
import { renderApp } from '../../../tests/renderApp'
import { server } from '../../../tests/server'

describe('bootstrap e rotas', () => {
  it('mantem loading ate concluir o bootstrap autenticado', async () => {
    server.use(
      http.get(`${apiBaseUrl}/auth/csrf/`, () => HttpResponse.json({ csrfToken: 'csrf' })),
      http.post(`${apiBaseUrl}/auth/refresh/`, async () => {
        await delay(30)
        return HttpResponse.json({ access: 'boot-access', token_type: 'Bearer', expires_in: 300 })
      }),
      http.get(`${apiBaseUrl}/users/me/`, () => HttpResponse.json(testUser)),
    )
    renderApp('/app')
    expect(screen.getByRole('status')).toHaveTextContent('Validando sua sessao')
    expect(await screen.findByRole('heading', { name: /Ola, Ana/i })).toBeInTheDocument()
  })

  it('restaura a sessao pelo refresh e users/me', async () => {
    mockAuthenticatedBootstrap()
    renderApp('/app')
    expect(await screen.findByText('Sessao autenticada')).toBeInTheDocument()
    expect(getAccessToken()).toBe('boot-access')
  })

  it('redireciona rota privada sem refresh para login', async () => {
    mockUnauthenticatedBootstrap()
    renderApp('/app')
    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
  })

  it('redireciona usuario autenticado para fora do login', async () => {
    mockAuthenticatedBootstrap()
    renderApp('/login')
    expect(await screen.findByText('Sessao autenticada')).toBeInTheDocument()
  })

  it('exibe fallback 404', () => {
    mockUnauthenticatedBootstrap()
    renderApp('/nao-existe')
    expect(screen.getByRole('heading', { name: 'Pagina nao encontrada' })).toBeInTheDocument()
  })
})

describe('login', () => {
  it('valida campos localmente sem chamar o backend', async () => {
    mockUnauthenticatedBootstrap()
    let loginCalls = 0
    server.use(http.post(`${apiBaseUrl}/auth/login/`, () => {
      loginCalls += 1
      return new HttpResponse(null, { status: 500 })
    }))
    renderApp('/login')
    await screen.findByRole('heading', { name: 'Entre na sua conta' })
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByText('Informe seu usuario.')).toBeInTheDocument()
    expect(screen.getByText('Informe sua senha.')).toBeInTheDocument()
    expect(loginCalls).toBe(0)
  })

  it('autentica, guarda usuario e access somente em memoria', async () => {
    mockUnauthenticatedBootstrap()
    server.use(
      http.post(`${apiBaseUrl}/auth/login/`, () =>
        HttpResponse.json({ access: 'login-access', token_type: 'Bearer', expires_in: 300, user: testUser }),
      ),
    )
    renderApp('/login')
    await screen.findByRole('heading', { name: 'Entre na sua conta' })
    await userEvent.type(screen.getByLabelText('Usuario'), 'ana')
    await userEvent.type(screen.getByLabelText('Senha'), 'segredo')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('heading', { name: /Ola, Ana/i })).toBeInTheDocument()
    expect(getAccessToken()).toBe('login-access')
    expect(localStorage.length).toBe(0)
    expect(sessionStorage.length).toBe(0)
  })

  it.each([
    [401, 'Credenciais invalidas.'],
    [429, 'Muitas tentativas.'],
  ])('mostra erro amigavel do backend para status %s', async (status, message) => {
    mockUnauthenticatedBootstrap()
    server.use(
      http.post(`${apiBaseUrl}/auth/login/`, () =>
        HttpResponse.json({ status, code: status === 429 ? 'throttled' : 'authentication_failed', message, errors: null }, { status }),
      ),
    )
    renderApp('/login')
    await screen.findByRole('heading', { name: 'Entre na sua conta' })
    await userEvent.type(screen.getByLabelText('Usuario'), 'ana')
    await userEvent.type(screen.getByLabelText('Senha'), 'errada')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent(message)
  })

  it('desabilita o botao durante o envio', async () => {
    mockUnauthenticatedBootstrap()
    server.use(
      http.post(`${apiBaseUrl}/auth/login/`, async () => {
        await delay(50)
        return HttpResponse.json({ access: 'login-access', token_type: 'Bearer', expires_in: 300, user: testUser })
      }),
    )
    renderApp('/login')
    await screen.findByRole('heading', { name: 'Entre na sua conta' })
    await userEvent.type(screen.getByLabelText('Usuario'), 'ana')
    await userEvent.type(screen.getByLabelText('Senha'), 'segredo')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(screen.getByRole('button', { name: 'Entrando...' })).toBeDisabled()
    expect(await screen.findByText('Sessao autenticada')).toBeInTheDocument()
  })

  it('rejeita resposta de login invalida sem guardar token', async () => {
    mockUnauthenticatedBootstrap()
    server.use(http.post(`${apiBaseUrl}/auth/login/`, () => HttpResponse.json({ access: '', user: testUser })))
    renderApp('/login')
    await screen.findByRole('heading', { name: 'Entre na sua conta' })
    await userEvent.type(screen.getByLabelText('Usuario'), 'ana')
    await userEvent.type(screen.getByLabelText('Senha'), 'segredo')
    await userEvent.click(screen.getByRole('button', { name: 'Entrar' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('formato inesperado')
    expect(getAccessToken()).toBeNull()
  })
})

describe('logout', () => {
  it('envia CSRF, limpa estado e redireciona mesmo com estado local ativo', async () => {
    mockAuthenticatedBootstrap()
    let csrfHeader: string | null = null
    server.use(
      http.post(`${apiBaseUrl}/auth/logout/`, ({ request }) => {
        csrfHeader = request.headers.get('x-csrftoken')
        return new HttpResponse(null, { status: 204 })
      }),
    )
    renderApp('/app')
    await screen.findByText('Sessao autenticada')
    await userEvent.click(screen.getByRole('button', { name: 'Sair' }))
    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
    expect(csrfHeader).toBe('csrf-test')
    expect(getAccessToken()).toBeNull()
  })

  it('limpa a interface mesmo se o backend rejeitar logout', async () => {
    mockAuthenticatedBootstrap()
    server.use(http.post(`${apiBaseUrl}/auth/logout/`, () => new HttpResponse(null, { status: 401 })))
    renderApp('/app')
    await screen.findByText('Sessao autenticada')
    await userEvent.click(screen.getByRole('button', { name: 'Sair' }))
    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })
})
