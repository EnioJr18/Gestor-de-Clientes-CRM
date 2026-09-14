import { http, HttpResponse } from 'msw'
import { act, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'

import { getAccessToken } from '../../../lib/api/tokenStore'
import { apiBaseUrl, mockAuthenticatedBootstrap, mockUnauthenticatedBootstrap, testUser } from '../../../tests/authHandlers'
import { renderApp } from '../../../tests/renderApp'
import { server } from '../../../tests/server'

async function fillRegistrationForm() {
  await userEvent.type(screen.getByLabelText('Nome de usuario'), 'nova-conta')
  await userEvent.type(screen.getByLabelText('E-mail'), 'nova@example.com')
  await userEvent.type(screen.getByLabelText('Nome'), 'Nova')
  await userEvent.type(screen.getByLabelText('Sobrenome'), 'Conta')
  await userEvent.type(screen.getByLabelText('Senha'), 'StrongPass123!')
  await userEvent.type(screen.getByLabelText('Confirmar senha'), 'StrongPass123!')
}

describe('cadastro publico', () => {
  it('renderiza, valida os campos e permite voltar ao login', async () => {
    mockUnauthenticatedBootstrap()
    renderApp('/register')

    expect(await screen.findByRole('heading', { name: 'Crie sua conta' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Criar minha conta' }))
    expect(await screen.findByText('Informe seu nome de usuario.')).toBeInTheDocument()
    expect(screen.getByText('Informe um e-mail valido.')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('link', { name: 'Entrar' }))
    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
  })

  it('rejeita confirmacao divergente sem enviar a requisicao', async () => {
    mockUnauthenticatedBootstrap()
    let requests = 0
    server.use(http.post(`${apiBaseUrl}/auth/register/`, () => { requests += 1; return new HttpResponse(null, { status: 500 }) }))
    renderApp('/register')

    await screen.findByRole('heading', { name: 'Crie sua conta' })
    await fillRegistrationForm()
    await userEvent.clear(screen.getByLabelText('Confirmar senha'))
    await userEvent.type(screen.getByLabelText('Confirmar senha'), 'DifferentPass123!')
    await userEvent.click(screen.getByRole('button', { name: 'Criar minha conta' }))

    expect(await screen.findByText('As senhas devem coincidir.')).toBeInTheDocument()
    expect(requests).toBe(0)
  })

  it('mostra erro da API e redireciona para login apos sucesso', async () => {
    mockUnauthenticatedBootstrap()
    server.use(http.post(`${apiBaseUrl}/auth/register/`, () => HttpResponse.json({ status: 400, code: 'validation_error', message: 'Dados invalidos.', errors: { username: ['Este nome de usuario ja existe.'] } }, { status: 400 })))
    renderApp('/register')

    await screen.findByRole('heading', { name: 'Crie sua conta' })
    await fillRegistrationForm()
    await userEvent.click(screen.getByRole('button', { name: 'Criar minha conta' }))
    expect(await screen.findByText('Este nome de usuario ja existe.')).toBeInTheDocument()

    server.use(http.post(`${apiBaseUrl}/auth/register/`, () => HttpResponse.json({ ...testUser, username: 'nova-conta' }, { status: 201 })))
    await userEvent.click(screen.getByRole('button', { name: 'Criar minha conta' }))
    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
    expect(screen.getByText('Conta criada com sucesso. Entre para continuar.')).toBeInTheDocument()
  })
})

describe('perfil autenticado', () => {
  it('protege a rota de perfil para usuarios nao autenticados', async () => {
    mockUnauthenticatedBootstrap()
    renderApp('/app/profile')
    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
  })

  it('redireciona usuarios autenticados para fora do cadastro', async () => {
    mockAuthenticatedBootstrap()
    renderApp('/register')
    await waitFor(() => expect(getAccessToken()).toBe('boot-access'))
    await act(async () => { await vi.dynamicImportSettled() })
    expect(await screen.findByRole('heading', { name: 'Dashboard' })).toBeInTheDocument()
  })

  it('carrega os dados, salva o perfil e atualiza o nome no layout', async () => {
    mockAuthenticatedBootstrap()
    const updatedUser = { ...testUser, username: 'ana-nova', first_name: 'Ana Nova', last_name: 'Oliveira', email: 'ana.nova@example.com' }
    let payload: unknown
    server.use(http.patch(`${apiBaseUrl}/users/me/`, async ({ request }) => { payload = await request.json(); return HttpResponse.json(updatedUser) }))
    renderApp('/app/profile')

    expect(await screen.findByRole('heading', { name: 'Meu perfil' })).toBeInTheDocument()
    expect(screen.getByLabelText('Nome de usuario')).toHaveValue('ana')
    await userEvent.clear(screen.getByLabelText('Nome'))
    await userEvent.type(screen.getByLabelText('Nome'), 'Ana Nova')
    await userEvent.clear(screen.getByLabelText('Sobrenome'))
    await userEvent.type(screen.getByLabelText('Sobrenome'), 'Oliveira')
    await userEvent.clear(screen.getByLabelText('E-mail'))
    await userEvent.type(screen.getByLabelText('E-mail'), 'ana.nova@example.com')
    await userEvent.clear(screen.getByLabelText('Nome de usuario'))
    await userEvent.type(screen.getByLabelText('Nome de usuario'), 'ana-nova')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar dados' }))

    await waitFor(() => expect(payload).toEqual({ username: 'ana-nova', first_name: 'Ana Nova', last_name: 'Oliveira', email: 'ana.nova@example.com' }))
    expect(await screen.findByText('Dados da conta atualizados.')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Ana Nova/ })).toBeInTheDocument()
  })

  it('exibe erros de validacao e de API ao atualizar o perfil', async () => {
    mockAuthenticatedBootstrap()
    server.use(http.patch(`${apiBaseUrl}/users/me/`, () => HttpResponse.json({ status: 400, code: 'validation_error', message: 'Dados invalidos.', errors: { username: ['Este nome de usuario ja existe.'] } }, { status: 400 })))
    renderApp('/app/profile')

    await screen.findByRole('heading', { name: 'Meu perfil' })
    await userEvent.clear(screen.getByLabelText('Nome de usuario'))
    await userEvent.type(screen.getByLabelText('Nome de usuario'), 'duplicado')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar dados' }))
    expect(await screen.findByText('Este nome de usuario ja existe.')).toBeInTheDocument()
  })
})

describe('alteracao de senha', () => {
  async function openProfile() {
    mockAuthenticatedBootstrap()
    renderApp('/app/profile')
    await screen.findByRole('heading', { name: 'Meu perfil' })
  }

  async function fillPasswordForm(confirm = 'ReplacementPass123!') {
    await userEvent.type(screen.getByLabelText('Senha atual'), 'CurrentPass123!')
    await userEvent.type(screen.getByLabelText('Nova senha'), 'ReplacementPass123!')
    await userEvent.type(screen.getByLabelText('Confirmar nova senha'), confirm)
  }

  it('valida a confirmacao antes de chamar a API', async () => {
    await openProfile()
    await fillPasswordForm('DifferentPass123!')
    await userEvent.click(screen.getByRole('button', { name: 'Alterar senha' }))
    expect(await screen.findByText('As senhas devem coincidir.')).toBeInTheDocument()
  })

  it('mostra erro da API para senha atual incorreta', async () => {
    await openProfile()
    server.use(http.post(`${apiBaseUrl}/auth/change-password/`, () => HttpResponse.json({ status: 400, code: 'validation_error', message: 'Dados invalidos.', errors: { current_password: ['Senha atual incorreta.'] } }, { status: 400 })))
    await fillPasswordForm()
    await userEvent.click(screen.getByRole('button', { name: 'Alterar senha' }))
    expect(await screen.findByText('Senha atual incorreta.')).toBeInTheDocument()
  })

  it('encerra o estado local e redireciona para login apos sucesso', async () => {
    await openProfile()
    server.use(http.post(`${apiBaseUrl}/auth/change-password/`, () => new HttpResponse(null, { status: 204 })))
    expect(getAccessToken()).toBe('boot-access')
    await fillPasswordForm()
    await userEvent.click(screen.getByRole('button', { name: 'Alterar senha' }))

    expect(await screen.findByRole('heading', { name: 'Entre na sua conta' })).toBeInTheDocument()
    expect(screen.getByText('Senha alterada com sucesso. Entre novamente para continuar.')).toBeInTheDocument()
    expect(getAccessToken()).toBeNull()
  })
})
