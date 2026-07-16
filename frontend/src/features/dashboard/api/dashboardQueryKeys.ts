import type { DashboardFilters } from '../types/dashboard'
export const dashboardQueryKeys = { all: ['dashboard'] as const, summaries: () => [...dashboardQueryKeys.all, 'summary'] as const, summary: (filters: DashboardFilters) => [...dashboardQueryKeys.summaries(), filters] as const }
