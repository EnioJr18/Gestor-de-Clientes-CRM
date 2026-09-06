import { format, isValid, parseISO } from 'date-fns'
import type { DashboardInteractionTypeItem } from '../types/dashboard'

export const interactionTypeLabels: Record<DashboardInteractionTypeItem['tipo'], string> = {
  LIGACAO: 'Ligacao',
  EMAIL: 'E-mail',
  REUNIAO: 'Reuniao',
  MENSAGEM: 'Mensagem',
  NOTA: 'Nota',
}

export function interactionTypeLabel(tipo: DashboardInteractionTypeItem['tipo']): string { return interactionTypeLabels[tipo] }

export function formatDashboardDate(value: string): string { const date = parseISO(value); return isValid(date) ? format(date, "dd/MM/yyyy 'as' HH:mm") : 'Data indisponivel' }
export function leadFullName(nome: string, sobrenome: string | null): string { return [nome, sobrenome].filter(Boolean).join(' ') }
