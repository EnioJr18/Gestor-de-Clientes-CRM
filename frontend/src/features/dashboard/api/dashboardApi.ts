import { apiClient } from '../../../lib/api/client'
import { dashboardSummarySchema } from '../schemas/dashboardSchema'
import type { DashboardFilters, DashboardSummary } from '../types/dashboard'
function paramsFromFilters(filters: DashboardFilters) { return { period: filters.period, ...(filters.period === 'custom' && filters.date_from ? { date_from: filters.date_from } : {}), ...(filters.period === 'custom' && filters.date_to ? { date_to: filters.date_to } : {}) } }
export async function getDashboardSummary(filters: DashboardFilters): Promise<DashboardSummary> { const response = await apiClient.get('/dashboard/summary/', { params: paramsFromFilters(filters) }); return dashboardSummarySchema.parse(response.data) }
