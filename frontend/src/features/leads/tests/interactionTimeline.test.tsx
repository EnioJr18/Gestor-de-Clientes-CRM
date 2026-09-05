import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { delay, http, HttpResponse } from 'msw'
import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import { apiBaseUrl } from '../../../tests/authHandlers'
import { server } from '../../../tests/server'
import { InteractionTimeline } from '../components/InteractionTimeline'
import type { Interaction } from '../types/interaction'

const leadId = 7
const first: Interaction = { id: 12, tipo: 'LIGACAO', data_interacao: '2026-09-04T17:30:00Z', nota: 'Ligacao mais recente.', criado_em: '2026-09-04T17:31:00Z', atualizado_em: '2026-09-04T17:31:00Z' }
const second: Interaction = { id: 11, tipo: 'EMAIL', data_interacao: '2026-09-03T17:30:00Z', nota: 'E-mail anterior.', criado_em: '2026-09-03T17:31:00Z', atualizado_em: '2026-09-03T17:31:00Z' }

function list(results: Interaction[]) {
  return { count: results.length, next: null, previous: null, results }
}

function renderTimeline() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(<QueryClientProvider client={client}><InteractionTimeline leadId={leadId} /></QueryClientProvider>)
}

describe('timeline de interacoes', () => {
  it('mostra loading e estado vazio com acao para registrar', async () => {
    server.use(http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, async () => { await delay(30); return HttpResponse.json(list([])) }))
    renderTimeline()
    expect(screen.getByLabelText('Carregando interacoes')).toBeInTheDocument()
    expect(await screen.findByText('Nenhuma interacao registrada.')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Registrar interacao' })).toBeInTheDocument()
  })

  it('exibe os tipos, datas, observacoes e ordem recebida da API', async () => {
    server.use(http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, () => HttpResponse.json(list([first, second]))))
    renderTimeline()
    expect(await screen.findByText('Ligacao mais recente.')).toBeInTheDocument()
    expect(screen.getByText('E-mail anterior.')).toBeInTheDocument()
    expect(screen.getByText('Ligacao')).toBeInTheDocument()
    expect(screen.getByText('E-mail')).toBeInTheDocument()
    expect(screen.getByText(/04\/09\/2026/)).toBeInTheDocument()
    const notes = screen.getAllByText(/(Ligacao mais recente|E-mail anterior)/).map((node) => node.textContent)
    expect(notes).toEqual(['Ligacao mais recente.', 'E-mail anterior.'])
  })

  it('mostra erro normalizado e permite tentar novamente', async () => {
    let healthy = false
    server.use(http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, () => healthy ? HttpResponse.json(list([first])) : HttpResponse.json({ status: 500 }, { status: 500 })))
    renderTimeline()
    expect(await screen.findByRole('alert')).toHaveTextContent('Nao foi possivel carregar as interacoes.')
    healthy = true
    await userEvent.click(screen.getByRole('button', { name: 'Tentar novamente' }))
    expect(await screen.findByText('Ligacao mais recente.')).toBeInTheDocument()
  })

  it('cria interacao, envia payload tipado, atualiza timeline e fecha dialogo', async () => {
    const records: Interaction[] = []
    let payload: Record<string, unknown> = {}
    server.use(
      http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, () => HttpResponse.json(list(records))),
      http.post(`${apiBaseUrl}/leads/${leadId}/interactions/`, async ({ request }) => {
        payload = await request.json() as Record<string, unknown>
        const created: Interaction = { id: 13, tipo: payload.tipo as Interaction['tipo'], data_interacao: payload.data_interacao as string, nota: payload.nota as string, criado_em: '2026-09-04T18:00:00Z', atualizado_em: '2026-09-04T18:00:00Z' }
        records.unshift(created)
        return HttpResponse.json(created, { status: 201 })
      }),
    )
    renderTimeline()
    await screen.findByText('Nenhuma interacao registrada.')
    await userEvent.click(screen.getByRole('button', { name: 'Registrar interacao' }))
    const dialog = screen.getByRole('dialog', { name: 'Registrar interacao' })
    expect(dialog).toBeInTheDocument()
    await userEvent.clear(screen.getByLabelText('Observacao'))
    await userEvent.type(screen.getByLabelText('Observacao'), 'Retorno combinado.')
    await userEvent.selectOptions(screen.getByLabelText('Tipo'), 'MENSAGEM')
    await userEvent.click(within(dialog).getByRole('button', { name: 'Registrar interacao' }))
    await waitFor(() => expect(payload).toMatchObject({ tipo: 'MENSAGEM', nota: 'Retorno combinado.' }))
    expect(String(payload.data_interacao)).toMatch(/^\d{4}-\d{2}-\d{2}T/)
    expect(new Date(String(payload.data_interacao)).toString()).not.toBe('Invalid Date')
    expect(await screen.findByText('Retorno combinado.')).toBeInTheDocument()
    expect(screen.queryByRole('dialog', { name: 'Registrar interacao' })).not.toBeInTheDocument()
  })

  it('valida observacao antes de enviar', async () => {
    server.use(http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, () => HttpResponse.json(list([]))))
    renderTimeline()
    await screen.findByText('Nenhuma interacao registrada.')
    await userEvent.click(screen.getByRole('button', { name: 'Registrar interacao' }))
    await userEvent.click(within(screen.getByRole('dialog', { name: 'Registrar interacao' })).getByRole('button', { name: 'Registrar interacao' }))
    expect(await screen.findByText('Informe a observacao.')).toBeInTheDocument()
  })

  it('edita uma interacao com PATCH e atualiza a timeline', async () => {
    const records = [first]
    let patched = false
    server.use(
      http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, () => HttpResponse.json(list(records))),
      http.patch(`${apiBaseUrl}/leads/${leadId}/interactions/${first.id}/`, async ({ request }) => {
        const payload = await request.json() as Partial<Interaction>
        records[0] = { ...records[0], ...payload, atualizado_em: '2026-09-04T18:00:00Z' }
        patched = true
        return HttpResponse.json(records[0])
      }),
    )
    renderTimeline()
    await screen.findByText('Ligacao mais recente.')
    await userEvent.click(screen.getByRole('button', { name: /Editar interacao de Ligacao/i }))
    await userEvent.clear(screen.getByLabelText('Observacao'))
    await userEvent.type(screen.getByLabelText('Observacao'), 'Ligacao atualizada.')
    await userEvent.click(screen.getByRole('button', { name: 'Salvar alteracoes' }))
    await waitFor(() => expect(patched).toBe(true))
    expect(await screen.findByText('Ligacao atualizada.')).toBeInTheDocument()
  })

  it('confirma exclusao antes de enviar DELETE e remove o item', async () => {
    const records = [first]
    let calls = 0
    server.use(
      http.get(`${apiBaseUrl}/leads/${leadId}/interactions/`, () => HttpResponse.json(list(records))),
      http.delete(`${apiBaseUrl}/leads/${leadId}/interactions/${first.id}/`, () => { calls += 1; records.splice(0, 1); return new HttpResponse(null, { status: 204 }) }),
    )
    renderTimeline()
    await screen.findByText('Ligacao mais recente.')
    await userEvent.click(screen.getByRole('button', { name: /Excluir interacao de Ligacao/i }))
    expect(screen.getByRole('dialog', { name: 'Excluir interacao' })).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: 'Cancelar' }))
    expect(calls).toBe(0)
    await userEvent.click(screen.getByRole('button', { name: /Excluir interacao de Ligacao/i }))
    await userEvent.click(screen.getByRole('button', { name: 'Excluir interacao' }))
    await waitFor(() => expect(calls).toBe(1))
    expect(await screen.findByText('Nenhuma interacao registrada.')).toBeInTheDocument()
  })
})
