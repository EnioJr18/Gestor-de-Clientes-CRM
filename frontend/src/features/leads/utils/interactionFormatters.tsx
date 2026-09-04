import { CalendarDays, Mail, MessageCircle, Phone, StickyNote, type LucideIcon } from 'lucide-react'
import { format, isValid, parseISO } from 'date-fns'
import { ptBR } from 'date-fns/locale'

import type { InteractionType } from '../types/interaction'

export const interactionPresentation: Record<InteractionType, { label: string; Icon: LucideIcon }> = {
  LIGACAO: { label: 'Ligacao', Icon: Phone },
  EMAIL: { label: 'E-mail', Icon: Mail },
  REUNIAO: { label: 'Reuniao', Icon: CalendarDays },
  MENSAGEM: { label: 'Mensagem', Icon: MessageCircle },
  NOTA: { label: 'Nota', Icon: StickyNote },
}

export function formatInteractionDate(value: string): string {
  const date = parseISO(value)
  return isValid(date) ? format(date, "dd/MM/yyyy 'as' HH:mm", { locale: ptBR }) : 'Data indisponivel'
}

export function toDateTimeLocalValue(value: string): string {
  const date = parseISO(value)
  return isValid(date) ? format(date, "yyyy-MM-dd'T'HH:mm") : format(new Date(), "yyyy-MM-dd'T'HH:mm")
}
