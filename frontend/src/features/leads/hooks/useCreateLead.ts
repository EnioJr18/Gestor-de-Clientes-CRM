import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createLead } from '../api/leadsApi'
import { leadQueryKeys } from '../api/leadQueryKeys'
export function useCreateLead() { const client = useQueryClient(); return useMutation({ mutationFn: createLead, onSuccess: () => client.invalidateQueries({ queryKey: leadQueryKeys.lists() }) }) }
