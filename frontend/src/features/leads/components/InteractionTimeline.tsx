import { Pencil, Plus, Trash2 } from 'lucide-react'
import { useState } from 'react'

import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { usePrefersReducedMotion } from '../../../lib/hooks/usePrefersReducedMotion'
import { useInteractions } from '../hooks/useInteractions'
import type { Interaction } from '../types/interaction'
import { formatInteractionDate, interactionPresentation } from '../utils/interactionFormatters'
import { DeleteInteractionDialog } from './DeleteInteractionDialog'
import { InteractionFormDialog } from './InteractionFormDialog'

export function InteractionTimeline({ leadId }: { leadId: number }) {
  const query = useInteractions(leadId)
  const reducedMotion = usePrefersReducedMotion()
  const [creating, setCreating] = useState(false)
  const [editing, setEditing] = useState<Interaction | undefined>()
  const [deleting, setDeleting] = useState<Interaction | undefined>()
  const [feedback, setFeedback] = useState<string | null>(null)

  function succeeded(message: string) {
    setFeedback(message)
  }

  return <section className="mt-8 border-t border-line pt-6" aria-labelledby="interactions-heading">
    <div className="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 id="interactions-heading" className="text-xl font-semibold text-strong">Historico de interacoes</h2>
        <p className="mt-1 text-sm text-muted">Registros de contato e acompanhamentos deste lead.</p>
      </div>
      <button className="primary-button w-auto" type="button" onClick={() => setCreating(true)}><Plus className="size-4" aria-hidden="true" />Registrar interacao</button>
    </div>
    {feedback && <p className="mt-4 text-sm text-success" role="status">{feedback}</p>}
    {query.isLoading && <TimelineSkeleton />}
    {query.isError && <TimelineError message={normalizeApiError(query.error).message} onRetry={() => void query.refetch()} />}
    {query.data && query.data.count === 0 && <div className="mt-6 border-l-2 border-brand pl-4"><p className="font-medium text-strong">Nenhuma interacao registrada.</p><p className="mt-1 text-sm text-muted">Registre o primeiro contato para iniciar este historico.</p></div>}
    {query.data && query.data.count > 0 && <ol className="mt-6 space-y-5 border-l border-line pl-5" aria-label="Timeline de interacoes">
      {query.data.results.map((interaction) => <TimelineItem key={interaction.id} interaction={interaction} animated={!reducedMotion} onEdit={() => setEditing(interaction)} onDelete={() => setDeleting(interaction)} />)}
    </ol>}
    {creating && <InteractionFormDialog leadId={leadId} onClose={() => setCreating(false)} onSuccess={succeeded} />}
    {editing && <InteractionFormDialog leadId={leadId} interaction={editing} onClose={() => setEditing(undefined)} onSuccess={succeeded} />}
    {deleting && <DeleteInteractionDialog leadId={leadId} interaction={deleting} onClose={() => setDeleting(undefined)} onSuccess={() => { setDeleting(undefined); succeeded('Interacao excluida com sucesso.') }} />}
  </section>
}

function TimelineItem({ interaction, animated, onEdit, onDelete }: { interaction: Interaction; animated: boolean; onEdit: () => void; onDelete: () => void }) {
  const presentation = interactionPresentation[interaction.tipo]
  const { Icon } = presentation
  const timestamp = formatInteractionDate(interaction.data_interacao)
  return <li className={`relative ${animated ? 'timeline-item' : ''}`}>
    <span className="absolute -left-8 top-1 grid size-5 place-items-center rounded-full border border-brand bg-panel text-brand"><Icon className="size-3" aria-hidden="true" /></span>
    <article>
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-medium text-strong">{presentation.label}</p>
          <time className="mt-1 block text-sm text-muted" dateTime={interaction.data_interacao}>{timestamp}</time>
        </div>
        <div className="flex gap-2">
          <button className="icon-button" type="button" aria-label={`Editar interacao de ${presentation.label} em ${timestamp}`} onClick={onEdit}><Pencil className="size-4" aria-hidden="true" /></button>
          <button className="icon-button danger-icon-button" type="button" aria-label={`Excluir interacao de ${presentation.label} em ${timestamp}`} onClick={onDelete}><Trash2 className="size-4" aria-hidden="true" /></button>
        </div>
      </div>
      <p className="mt-3 whitespace-pre-wrap text-sm leading-6 text-strong">{interaction.nota}</p>
    </article>
  </li>
}

function TimelineSkeleton() {
  return <div className="mt-6 space-y-5 border-l border-line pl-5" aria-label="Carregando interacoes">
    <div className="skeleton h-20" /><div className="skeleton h-20" />
  </div>
}

function TimelineError({ message, onRetry }: { message: string; onRetry: () => void }) {
  return <div className="mt-6 border-l-2 border-danger pl-4" role="alert"><p className="font-medium text-strong">Nao foi possivel carregar as interacoes.</p><p className="mt-1 text-sm text-muted">{message}</p><button className="secondary-button mt-4" type="button" onClick={onRetry}>Tentar novamente</button></div>
}
