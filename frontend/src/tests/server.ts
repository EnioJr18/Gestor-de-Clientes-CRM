import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

const emptyDashboard = {
  period: { key: '30d', date_from: '2026-06-16', date_to: '2026-07-15' },
  metrics: { total_leads: 0, created_today: 0, created_in_period: 0, converted_in_period: 0, conversion_rate: 0 },
  by_status: [], by_priority: [], monthly_evolution: [], recent_leads: [],
}

export const server = setupServer(
  http.get('http://localhost:8000/api/v1/dashboard/summary/', () => HttpResponse.json(emptyDashboard)),
  http.get('http://localhost:8000/api/v1/leads/:leadId/interactions/', () => HttpResponse.json({ count: 0, next: null, previous: null, results: [] })),
)
