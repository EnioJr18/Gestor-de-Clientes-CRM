import { apiClient } from '../../../lib/api/client'
import { interactionListResponseSchema, interactionSchema } from '../schemas/interactionSchema'
import type { Interaction, InteractionListResponse, InteractionPayload, UpdateInteractionPayload } from '../types/interaction'

function interactionsPath(leadId: number): string {
  return `/leads/${leadId}/interactions/`
}

export async function getInteractions(leadId: number): Promise<InteractionListResponse> {
  const response = await apiClient.get(interactionsPath(leadId))
  return interactionListResponseSchema.parse(response.data)
}

export async function createInteraction(leadId: number, payload: InteractionPayload): Promise<Interaction> {
  const response = await apiClient.post(interactionsPath(leadId), payload)
  return interactionSchema.parse(response.data)
}

export async function updateInteraction(leadId: number, interactionId: number, payload: UpdateInteractionPayload): Promise<Interaction> {
  const response = await apiClient.patch(`${interactionsPath(leadId)}${interactionId}/`, payload)
  return interactionSchema.parse(response.data)
}

export async function deleteInteraction(leadId: number, interactionId: number): Promise<void> {
  await apiClient.delete(`${interactionsPath(leadId)}${interactionId}/`)
}
