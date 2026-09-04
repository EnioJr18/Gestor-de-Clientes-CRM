import { z } from 'zod'
import { isValid, parse } from 'date-fns'

import { interactionTypes, type InteractionPayload } from '../types/interaction'

export const interactionSchema = z.object({
  id: z.number().int().positive(),
  tipo: z.enum(interactionTypes),
  data_interacao: z.string().datetime({ offset: true }),
  nota: z.string().trim().min(1).max(10_000),
  criado_em: z.string().datetime({ offset: true }),
  atualizado_em: z.string().datetime({ offset: true }),
})

export const interactionListResponseSchema = z.object({
  count: z.number().int().nonnegative(),
  next: z.string().nullable(),
  previous: z.string().nullable(),
  results: z.array(interactionSchema),
})

export const interactionFormSchema = z.object({
  tipo: z.enum(interactionTypes),
  dataInteracao: z.string().min(1, 'Informe a data e hora.').refine(
    (value) => isValid(parse(value, "yyyy-MM-dd'T'HH:mm", new Date())),
    'Informe uma data e hora validas.',
  ),
  nota: z.string().trim().min(1, 'Informe a observacao.').max(10_000, 'Use no maximo 10000 caracteres.'),
})

export type InteractionFormValues = z.infer<typeof interactionFormSchema>

export function toInteractionPayload(values: InteractionFormValues): InteractionPayload {
  return {
    tipo: values.tipo,
    data_interacao: parse(values.dataInteracao, "yyyy-MM-dd'T'HH:mm", new Date()).toISOString(),
    nota: values.nota.trim(),
  }
}
