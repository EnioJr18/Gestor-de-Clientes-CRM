import { useState } from 'react'

import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { useDeleteInteraction } from '../hooks/useDeleteInteraction'
import type { Interaction } from '../types/interaction'
import { formatInteractionDate, interactionPresentation } from '../utils/interactionFormatters'
import { Dialog } from './Dialog'

export function DeleteInteractionDialog({ leadId, interaction, onClose, onSuccess }: { leadId: number; interaction: Interaction; onClose: () => void; onSuccess: () => void }) {
  const deletion = useDeleteInteraction()
  const [message, setMessage] = useState<string | null>(null)

  function confirm() {
    setMessage(null)
    void deletion.mutateAsync({ leadId, interactionId: interaction.id }).then(onSuccess).catch((error: unknown) => setMessage(normalizeApiError(error).message))
  }

  const label = interactionPresentation[interaction.tipo].label
  return <Dialog title="Excluir interacao" onClose={onClose} busy={deletion.isPending}>
    <p className="text-muted">Deseja excluir a interacao de <strong className="text-strong">{label}</strong> registrada em {formatInteractionDate(interaction.data_interacao)}? Esta acao e irreversivel.</p>
    {message && <p className="mt-4 field-error" role="alert">{message}</p>}
    <div className="mt-6 flex flex-wrap justify-end gap-3">
      <button className="secondary-button" type="button" disabled={deletion.isPending} onClick={onClose}>Cancelar</button>
      <button className="danger-button" type="button" disabled={deletion.isPending} onClick={confirm}>{deletion.isPending ? 'Excluindo...' : 'Excluir interacao'}</button>
    </div>
  </Dialog>
}
