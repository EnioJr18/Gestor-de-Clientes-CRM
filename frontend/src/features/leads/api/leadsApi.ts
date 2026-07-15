import { apiClient } from '../../../lib/api/client'
import { leadListResponseSchema, leadSchema } from '../schemas/leadSchema'
import type { CreateLeadPayload, Lead, LeadFilters, LeadListResponse, UpdateLeadPayload } from '../types/lead'
function paramsFromFilters(filters: LeadFilters) { return { page: filters.page, page_size: filters.pageSize, ...(filters.search ? { search: filters.search } : {}), ...(filters.status ? { status: filters.status } : {}), ...(filters.prioridade ? { prioridade: filters.prioridade } : {}), ...(filters.criadoEmDe ? { criado_em_de: filters.criadoEmDe } : {}), ...(filters.criadoEmAte ? { criado_em_ate: filters.criadoEmAte } : {}), ...(filters.ordering ? { ordering: filters.ordering } : {}) } }
export async function getLeads(filters: LeadFilters): Promise<LeadListResponse> { const response = await apiClient.get('/leads/', { params: paramsFromFilters(filters) }); return leadListResponseSchema.parse(response.data) }
export async function getLead(id: number): Promise<Lead> { const response = await apiClient.get(`/leads/${id}/`); return leadSchema.parse(response.data) }
export async function createLead(payload: CreateLeadPayload): Promise<Lead> { const response = await apiClient.post('/leads/', payload); return leadSchema.parse(response.data) }
export async function updateLead(id: number, payload: UpdateLeadPayload): Promise<Lead> { const response = await apiClient.patch(`/leads/${id}/`, payload); return leadSchema.parse(response.data) }
export async function deleteLead(id: number): Promise<void> { await apiClient.delete(`/leads/${id}/`) }
