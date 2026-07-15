import { format, isValid, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import type { LeadPriority, LeadStatus } from '../types/lead'
export const statusLabels: Record<LeadStatus, string> = { NOVO: 'Novo', EM_NEGOCIACAO: 'Em negociacao', PROPOSTA_ENVIADA: 'Proposta enviada', VENDIDO: 'Vendido', PERDIDO: 'Perdido' }
export const priorityLabels: Record<LeadPriority, string> = { BAIXA: 'Baixa', MEDIA: 'Media', ALTA: 'Alta' }
export function leadFullName(lead: { nome: string; sobrenome: string | null }) { return [lead.nome, lead.sobrenome].filter(Boolean).join(' ') }
export function formatLeadDate(value: string) { const date = parseISO(value); return isValid(date) ? format(date, "dd/MM/yyyy 'as' HH:mm", { locale: ptBR }) : 'Data indisponivel' }
