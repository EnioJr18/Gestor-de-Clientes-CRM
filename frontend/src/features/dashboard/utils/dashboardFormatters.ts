import { format, isValid, parseISO } from 'date-fns'
export function formatDashboardDate(value: string): string { const date = parseISO(value); return isValid(date) ? format(date, "dd/MM/yyyy 'as' HH:mm") : 'Data indisponivel' }
export function leadFullName(nome: string, sobrenome: string | null): string { return [nome, sobrenome].filter(Boolean).join(' ') }
