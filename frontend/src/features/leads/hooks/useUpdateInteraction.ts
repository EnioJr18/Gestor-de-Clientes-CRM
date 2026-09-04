import { useMutation, useQueryClient } from '@tanstack/react-query'

import { dashboardQueryKeys } from '../../dashboard/api/dashboardQueryKeys'
import { updateInteraction } from '../api/interactionsApi'
import { interactionQueryKeys } from '../api/interactionQueryKeys'
import { leadQueryKeys } from '../api/leadQueryKeys'
import type { UpdateInteractionPayload } from '../types/interaction'

export function useUpdateInteraction() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, interactionId, payload }: { leadId: number; interactionId: number; payload: UpdateInteractionPayload }) => updateInteraction(leadId, interactionId, payload),
    onSuccess: (_, { leadId, interactionId }) => Promise.all([
      client.invalidateQueries({ queryKey: interactionQueryKeys.list(leadId) }),
      client.invalidateQueries({ queryKey: interactionQueryKeys.detail(leadId, interactionId) }),
      client.invalidateQueries({ queryKey: leadQueryKeys.detail(leadId) }),
      client.invalidateQueries({ queryKey: dashboardQueryKeys.all }),
    ]),
  })
}
