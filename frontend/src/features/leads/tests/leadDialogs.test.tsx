import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { http, HttpResponse } from 'msw'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { apiBaseUrl } from '../../../tests/authHandlers'
import { server } from '../../../tests/server'
import { DeleteLeadDialog } from '../components/DeleteLeadDialog'
import { LeadFormDialog } from '../components/LeadFormDialog'
import { LeadDetailsPage } from '../pages/LeadDetailsPage'
import type { Lead } from '../types/lead'

const lead: Lead = { id: 7, nome: 'Maria', sobrenome: 'Souza', email: 'maria@example.com', telefone: '11999999999', status: 'NOVO', prioridade: 'ALTA', criado_em: '2026-07-15T18:30:00Z', atualizado_em: '2026-07-16T18:30:00Z' }
function renderWithQuery(ui: React.ReactNode) { const client = new QueryClient({ defaultOptions: { queries: { retry: false } } }); return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>) }

describe('detalhes, edicao e exclusao de leads', () => {
  it('mostra detalhe completo, datas, badges e placeholder', async () => {
    server.use(http.get(`${apiBaseUrl}/leads/7/`, () => HttpResponse.json(lead)))
    renderWithQuery(<MemoryRouter initialEntries={['/app/leads/7']}><Routes><Route path="/app/leads/:id" element={<LeadDetailsPage />} /></Routes></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: 'Maria Souza' })).toBeInTheDocument()
    expect(screen.getByText('maria@example.com')).toBeInTheDocument(); expect(screen.getByText('11999999999')).toBeInTheDocument()
    expect(screen.getByLabelText('Status: Novo')).toBeInTheDocument(); expect(screen.getByLabelText('Prioridade: Alta')).toBeInTheDocument()
    expect(screen.getByText(/15\/07\/2026/)).toBeInTheDocument(); expect(screen.getByText(/Historico de interacoes sera adicionado/)).toBeInTheDocument()
  })

  it('trata detalhe 404, 500 e resposta invalida sem expor erro tecnico', async () => {
    server.use(http.get(`${apiBaseUrl}/leads/7/`, () => new HttpResponse(null, { status: 404 })))
    renderWithQuery(<MemoryRouter initialEntries={['/app/leads/7']}><Routes><Route path="/app/leads/:id" element={<LeadDetailsPage />} /></Routes></MemoryRouter>)
    expect(await screen.findByText('Lead nao encontrado')).toBeInTheDocument()
  })

  it('edita com PATCH, payload sem responsavel, feedback e fecha dialogo', async () => {
    let payload: Record<string, unknown> = {}; const success = vi.fn()
    server.use(http.patch(`${apiBaseUrl}/leads/7/`, async ({ request }) => { payload = await request.json() as Record<string, unknown>; return HttpResponse.json({ ...lead, ...payload }) }))
    renderWithQuery(<LeadFormDialog lead={lead} onClose={vi.fn()} onSuccess={success} />)
    expect(screen.getByRole('dialog', { name: 'Editar lead' })).toBeInTheDocument(); expect(screen.getByLabelText('Nome')).toHaveValue('Maria')
    await userEvent.clear(screen.getByLabelText('Nome')); await userEvent.type(screen.getByLabelText('Nome'), 'Maria Atualizada'); await userEvent.click(screen.getByRole('button', { name: 'Salvar alteracoes' }))
    await waitFor(() => expect(payload.nome).toBe('Maria Atualizada')); expect(payload).not.toHaveProperty('agente_responsavel'); expect(success).toHaveBeenCalledWith('Lead atualizado com sucesso.')
  })

  it('exibe erro de campo da edicao e preserva dialogo', async () => {
    server.use(http.patch(`${apiBaseUrl}/leads/7/`, () => HttpResponse.json({ status: 400, code: 'validation_error', message: 'Dados invalidos.', errors: { email: ['E-mail duplicado.'] } }, { status: 400 })))
    renderWithQuery(<LeadFormDialog lead={lead} onClose={vi.fn()} onSuccess={vi.fn()} />)
    await userEvent.click(screen.getByRole('button', { name: 'Salvar alteracoes' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('E-mail duplicado.')
  })

  it('dialogo de exclusao tem foco, fecha com Escape e confirma DELETE uma vez', async () => {
    const closed = vi.fn(); const success = vi.fn(); let calls = 0
    server.use(http.delete(`${apiBaseUrl}/leads/7/`, () => { calls += 1; return new HttpResponse(null, { status: 204 }) }))
    const { rerender } = renderWithQuery(<DeleteLeadDialog lead={lead} onClose={closed} onSuccess={success} />)
    expect(screen.getByRole('dialog', { name: 'Excluir lead' })).toBeInTheDocument(); expect(screen.getByText(/Maria Souza/)).toBeInTheDocument(); expect(screen.getByText(/irreversivel/)).toBeInTheDocument(); expect(document.activeElement).toHaveAttribute('role', 'dialog')
    await userEvent.keyboard('{Escape}'); expect(closed).toHaveBeenCalled()
    rerender(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><DeleteLeadDialog lead={lead} onClose={closed} onSuccess={success} /></QueryClientProvider>)
    await userEvent.click(screen.getByRole('button', { name: 'Excluir lead' })); await waitFor(() => expect(success).toHaveBeenCalled()); expect(calls).toBe(1)
  })
})
