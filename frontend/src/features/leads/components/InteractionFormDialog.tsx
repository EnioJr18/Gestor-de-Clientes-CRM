import { useState } from 'react'

import type { ApiError } from '../../auth/types/auth'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { useCreateInteraction } from '../hooks/useCreateInteraction'
import { useUpdateInteraction } from '../hooks/useUpdateInteraction'
import type { Interaction, InteractionPayload } from '../types/interaction'
import { Dialog } from './Dialog'
import { InteractionForm } from './InteractionForm'

export function InteractionFormDialog({ leadId, interaction, onClose, onSuccess }: { leadId: number; interaction?: Interaction; onClose: () => void; onSuccess: (message: string) => void }) {
  const create = useCreateInteraction()
  const update = useUpdateInteraction()
  const [error, setError] = useState<ApiError | null>(null)
  const saving = create.isPending || update.isPending

  function submit(payload: InteractionPayload) {
    setError(null)
    const mutation = interaction
      ? update.mutateAsync({ leadId, interactionId: interaction.id, payload })
      : create.mutateAsync({ leadId, payload })
    void mutation.then(() => {
      onSuccess(interaction ? 'Interacao atualizada com sucesso.' : 'Interacao registrada com sucesso.')
      onClose()
    }).catch((reason: unknown) => setError(normalizeApiError(reason)))
  }

  return <Dialog title={interaction ? 'Editar interacao' : 'Registrar interacao'} onClose={onClose}>
    <InteractionForm interaction={interaction} submitting={saving} error={error} onSubmit={submit} onCancel={onClose} />
  </Dialog>
}
