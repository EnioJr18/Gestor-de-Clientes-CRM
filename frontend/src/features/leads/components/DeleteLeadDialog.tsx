import { useState } from 'react'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { useDeleteLead } from '../hooks/useDeleteLead'
import type { Lead } from '../types/lead'
import { leadFullName } from '../utils/leadFormatters'
import { Dialog } from './Dialog'
export function DeleteLeadDialog({ lead, onClose, onSuccess }: { lead: Lead; onClose: () => void; onSuccess: () => void }) { const deletion = useDeleteLead(); const [message, setMessage] = useState<string | null>(null); function confirm() { setMessage(null); void deletion.mutateAsync(lead.id).then(onSuccess).catch((error: unknown) => setMessage(normalizeApiError(error).message)) }; return <Dialog title="Excluir lead" onClose={onClose}><p className="text-muted">Deseja excluir <strong className="text-strong">{leadFullName(lead)}</strong>? Esta acao e irreversivel.</p>{message && <p className="mt-4 field-error" role="alert">{message}</p>}<div className="mt-6 flex justify-end gap-3"><button className="secondary-button" type="button" disabled={deletion.isPending} onClick={onClose}>Cancelar</button><button className="danger-button" type="button" disabled={deletion.isPending} onClick={confirm}>{deletion.isPending ? 'Excluindo...' : 'Excluir lead'}</button></div></Dialog> }
