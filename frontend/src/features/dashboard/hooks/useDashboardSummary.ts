import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { getDashboardSummary } from '../api/dashboardApi'
import { dashboardQueryKeys } from '../api/dashboardQueryKeys'
import type { DashboardFilters } from '../types/dashboard'
export function useDashboardSummary(filters: DashboardFilters) { return useQuery({ queryKey: dashboardQueryKeys.summary(filters), queryFn: () => getDashboardSummary(filters), staleTime: 30_000, placeholderData: keepPreviousData, retry: (attempt, error) => { const normalized = normalizeApiError(error); return normalized.status !== 401 && normalized.code !== 'invalid_response' && attempt < 2 } }) }
