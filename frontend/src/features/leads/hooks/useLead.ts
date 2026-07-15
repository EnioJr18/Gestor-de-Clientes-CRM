import { useQuery } from '@tanstack/react-query'
import { getLead } from '../api/leadsApi'
import { leadQueryKeys } from '../api/leadQueryKeys'
export function useLead(id: number) { return useQuery({ queryKey: leadQueryKeys.detail(id), queryFn: () => getLead(id), enabled: Number.isInteger(id) && id > 0, meta: { private: true } }) }
