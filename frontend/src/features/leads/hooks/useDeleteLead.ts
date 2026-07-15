import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteLead } from '../api/leadsApi'
import { leadQueryKeys } from '../api/leadQueryKeys'
export function useDeleteLead() { const client = useQueryClient(); return useMutation({ mutationFn: deleteLead, onSuccess: (_, id) => Promise.all([client.removeQueries({ queryKey: leadQueryKeys.detail(id) }), client.invalidateQueries({ queryKey: leadQueryKeys.lists() })]) }) }
