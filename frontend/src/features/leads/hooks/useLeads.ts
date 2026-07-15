import { useQuery } from '@tanstack/react-query'
import { getLeads } from '../api/leadsApi'
import { leadQueryKeys } from '../api/leadQueryKeys'
import type { LeadFilters } from '../types/lead'
export function useLeads(filters: LeadFilters) { return useQuery({ queryKey: leadQueryKeys.list(filters), queryFn: () => getLeads(filters), meta: { private: true } }) }
