import { useMutation, useQueryClient } from '@tanstack/react-query'

import { dashboardQueryKeys } from '../../dashboard/api/dashboardQueryKeys'
import { deleteInteraction } from '../api/interactionsApi'
import { interactionQueryKeys } from '../api/interactionQueryKeys'
import { leadQueryKeys } from '../api/leadQueryKeys'

export function useDeleteInteraction() {
  const client = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, interactionId }: { leadId: number; interactionId: number }) => deleteInteraction(leadId, interactionId),
    onSuccess: (_, { leadId, interactionId }) => Promise.all([
      client.invalidateQueries({ queryKey: interactionQueryKeys.list(leadId) }),
      client.removeQueries({ queryKey: interactionQueryKeys.detail(leadId, interactionId) }),
      client.invalidateQueries({ queryKey: leadQueryKeys.detail(leadId) }),
      client.invalidateQueries({ queryKey: dashboardQueryKeys.all }),
    ]),
  })
}
