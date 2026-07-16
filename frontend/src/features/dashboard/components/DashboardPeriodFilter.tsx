import { CalendarDays } from 'lucide-react'
import { useState } from 'react'
import { dashboardFiltersSchema } from '../schemas/dashboardSchema'
import type { DashboardFilters, DashboardPeriodKey } from '../types/dashboard'

type DashboardPeriodFilterProps = { filters: DashboardFilters; onChange: (filters: DashboardFilters) => void }
const options: Array<{ value: DashboardPeriodKey; label: string }> = [{ value: '7d', label: 'Ultimos 7 dias' }, { value: '30d', label: 'Ultimos 30 dias' }, { value: '90d', label: 'Ultimos 90 dias' }, { value: '12m', label: 'Ultimos 12 meses' }]

export function DashboardPeriodFilter({ filters, onChange }: DashboardPeriodFilterProps) {
  const [dateFrom, setDateFrom] = useState(filters.date_from ?? '')
  const [dateTo, setDateTo] = useState(filters.date_to ?? '')
  const [customOpen, setCustomOpen] = useState(filters.period === 'custom')
  const [error, setError] = useState<string | null>(null)
  const apply = () => { const parsed = dashboardFiltersSchema.safeParse({ period: 'custom', date_from: dateFrom || undefined, date_to: dateTo || undefined }); if (!parsed.success) { setError(parsed.error.issues[0]?.message ?? 'Periodo invalido.'); return }; setError(null); onChange(parsed.data) }
  return <div className="rounded-xl border border-line bg-panel p-3"><label className="field-label" htmlFor="dashboard-period">Periodo</label><div className="flex flex-wrap items-end gap-3"><select id="dashboard-period" className="field-input max-w-xs py-2" value={customOpen ? 'custom' : filters.period} onChange={(event) => { const period = event.target.value as DashboardPeriodKey; setError(null); setCustomOpen(period === 'custom'); if (period !== 'custom') onChange({ period }) }}><option value="custom">Personalizado</option>{options.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}</select>{customOpen && <><label className="text-sm text-strong">Data inicial<input className="field-input mt-1 py-2" aria-label="Data inicial" type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} /></label><label className="text-sm text-strong">Data final<input className="field-input mt-1 py-2" aria-label="Data final" type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} /></label><button className="secondary-button" type="button" onClick={apply}><CalendarDays className="size-4" aria-hidden="true" />Aplicar</button></>}</div>{error && <p className="field-error" role="alert">{error}</p>}</div>
}
