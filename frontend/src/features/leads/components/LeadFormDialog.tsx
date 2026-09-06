import { useState } from 'react'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { useCreateLead } from '../hooks/useCreateLead'
import { useUpdateLead } from '../hooks/useUpdateLead'
import type { CreateLeadPayload, Lead } from '../types/lead'
import { Dialog } from './Dialog'
import { LeadForm } from './LeadForm'
import type { ApiError } from '../../auth/types/auth'
export function LeadFormDialog({ lead, onClose, onSuccess }: { lead?: Lead; onClose: () => void; onSuccess: (message: string) => void }) {
  const create = useCreateLead(); const update = useUpdateLead(); const [error, setError] = useState<ApiError | null>(null); const saving = create.isPending || update.isPending
  function submit(payload: CreateLeadPayload) { setError(null); const mutation = lead ? update.mutateAsync({ id: lead.id, payload }) : create.mutateAsync(payload); void mutation.then(() => { onSuccess(lead ? 'Lead atualizado com sucesso.' : 'Lead criado com sucesso.'); onClose() }).catch((reason: unknown) => setError(normalizeApiError(reason))) }
  return <Dialog title={lead ? 'Editar lead' : 'Criar lead'} onClose={onClose} busy={saving}><LeadForm lead={lead} submitting={saving} error={error} onSubmit={submit} onCancel={onClose} /></Dialog>
}
