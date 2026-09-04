import { useMutation, useQueryClient } from '@tanstack/react-query'

import { dashboardQueryKeys } from '../../dashboard/api/dashboardQueryKeys'
import { createInteraction } from '../api/interactionsApi'
import { interactionQueryKeys } from '../api/interactionQueryKeys'
import { leadQueryKeys } from '../api/leadQueryKeys'
import type { InteractionPayload } from '../types/interaction'

export function useCreateInteraction() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, payload }: { leadId: number; payload: InteractionPayload }) => createInteraction(leadId, payload),
    onSuccess: (_, { leadId }) => Promise.all([
      client.invalidateQueries({ queryKey: interactionQueryKeys.list(leadId) }),
      client.invalidateQueries({ queryKey: leadQueryKeys.detail(leadId) }),
      client.invalidateQueries({ queryKey: dashboardQueryKeys.all }),
    ]),
  })
}
