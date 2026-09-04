import { useQuery } from '@tanstack/react-query'

import { getInteractions } from '../api/interactionsApi'
import { interactionQueryKeys } from '../api/interactionQueryKeys'

export function useInteractions(leadId: number) {
  return useQuery({
    queryKey: interactionQueryKeys.list(leadId),
    queryFn: () => getInteractions(leadId),
    enabled: Number.isInteger(leadId) && leadId > 0,
    meta: { private: true },
  })
}
