import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateLead } from '../api/leadsApi'
import { leadQueryKeys } from '../api/leadQueryKeys'
import type { UpdateLeadPayload } from '../types/lead'
export function useUpdateLead() { const client = useQueryClient(); return useMutation({ mutationFn: ({ id, payload }: { id: number; payload: UpdateLeadPayload }) => updateLead(id, payload), onSuccess: (_, variables) => Promise.all([client.invalidateQueries({ queryKey: leadQueryKeys.detail(variables.id) }), client.invalidateQueries({ queryKey: leadQueryKeys.lists() })]) }) }
