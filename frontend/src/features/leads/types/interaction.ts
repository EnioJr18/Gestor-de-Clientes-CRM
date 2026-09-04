export const interactionTypes = ['LIGACAO', 'EMAIL', 'REUNIAO', 'MENSAGEM', 'NOTA'] as const

export type InteractionType = (typeof interactionTypes)[number]

export type Interaction = {
  id: number
  tipo: InteractionType
  data_interacao: string
  nota: string
  criado_em: string
  atualizado_em: string
}

export type InteractionListResponse = {
  count: number
  next: string | null
  previous: string | null
  results: Interaction[]
}

export type InteractionPayload = Pick<Interaction, 'tipo' | 'data_interacao' | 'nota'>

export type UpdateInteractionPayload = Partial<InteractionPayload>
