import type { LeadFilters } from '../types/lead'
export const leadQueryKeys = { all: ['leads'] as const, lists: () => [...leadQueryKeys.all, 'list'] as const, list: (filters: LeadFilters) => [...leadQueryKeys.lists(), filters] as const, details: () => [...leadQueryKeys.all, 'detail'] as const, detail: (id: number) => [...leadQueryKeys.details(), id] as const }
