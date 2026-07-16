import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createLead } from '../api/leadsApi'
import { leadQueryKeys } from '../api/leadQueryKeys'
import { dashboardQueryKeys } from '../../dashboard/api/dashboardQueryKeys'
export function useCreateLead() { const client = useQueryClient(); return useMutation({ mutationFn: createLead, onSuccess: () => Promise.all([client.invalidateQueries({ queryKey: leadQueryKeys.lists() }), client.invalidateQueries({ queryKey: dashboardQueryKeys.all })]) }) }
