export const interactionQueryKeys = {
  all: ['interactions'] as const,
  lists: () => [...interactionQueryKeys.all, 'list'] as const,
  list: (leadId: number) => [...interactionQueryKeys.lists(), leadId] as const,
  details: () => [...interactionQueryKeys.all, 'detail'] as const,
  detail: (leadId: number, interactionId: number) => [...interactionQueryKeys.details(), leadId, interactionId] as const,
}
