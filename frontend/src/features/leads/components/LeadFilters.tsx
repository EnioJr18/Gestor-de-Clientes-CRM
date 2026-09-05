import { Filter, Search, X } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Dialog } from './Dialog'
import { leadPriorities, leadStatuses, type LeadFilters, type LeadPriority, type LeadStatus } from '../types/lead'
import { priorityLabels, statusLabels } from '../utils/leadFormatters'

const orderingOptions = [
  ['-criado_em', 'Mais recentes'],
  ['criado_em', 'Mais antigos'],
  ['nome', 'Nome (A-Z)'],
  ['-nome', 'Nome (Z-A)'],
  ['prioridade', 'Prioridade (crescente)'],
  ['-prioridade', 'Prioridade (decrescente)'],
] as const

type LeadFiltersProps = {
  filters: LeadFilters
  onChange: (patch: Partial<LeadFilters>) => void
  onClear: () => void
}

function FilterControls({ filters, onChange }: Pick<LeadFiltersProps, 'filters' | 'onChange'>) {
  return <>
    <label><span className="field-label">Status</span><select className="field-input" value={filters.status || ''} onChange={(event) => onChange({ status: (event.target.value || undefined) as LeadStatus | undefined })}><option value="">Todos os status</option>{leadStatuses.map((status) => <option key={status} value={status}>{statusLabels[status]}</option>)}</select></label>
    <label><span className="field-label">Prioridade</span><select className="field-input" value={filters.prioridade || ''} onChange={(event) => onChange({ prioridade: (event.target.value || undefined) as LeadPriority | undefined })}><option value="">Todas as prioridades</option>{leadPriorities.map((priority) => <option key={priority} value={priority}>{priorityLabels[priority]}</option>)}</select></label>
    <label><span className="field-label">Ordenar por</span><select className="field-input" value={filters.ordering || '-criado_em'} onChange={(event) => onChange({ ordering: event.target.value as LeadFilters['ordering'] })}>{orderingOptions.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
    <label><span className="field-label">Criado a partir de</span><input className="field-input" type="date" value={filters.criadoEmDe || ''} onChange={(event) => onChange({ criadoEmDe: event.target.value || undefined })} /></label>
    <label><span className="field-label">Criado ate</span><input className="field-input" type="date" value={filters.criadoEmAte || ''} onChange={(event) => onChange({ criadoEmAte: event.target.value || undefined })} /></label>
  </>
}

export function LeadFilters({ filters, onChange, onClear }: LeadFiltersProps) {
  const [search, setSearch] = useState(filters.search || '')
  const [mobileOpen, setMobileOpen] = useState(false)
  const activeCount = [filters.search, filters.status, filters.prioridade, filters.criadoEmDe, filters.criadoEmAte, filters.ordering !== '-criado_em' ? filters.ordering : undefined].filter(Boolean).length
  useEffect(() => setSearch(filters.search || ''), [filters.search])
  useEffect(() => { const timer = window.setTimeout(() => { if (search !== (filters.search || '')) onChange({ search: search || undefined }) }, 400); return () => window.clearTimeout(timer) }, [search, filters.search, onChange])
  return <section className="rounded-2xl border border-line bg-panel p-4" aria-label="Filtros de leads">
    <div className="flex flex-col gap-3 md:flex-row md:items-center"><label className="relative flex-1"><span className="sr-only">Buscar leads</span><Search className="pointer-events-none absolute left-3 top-3.5 size-4 text-muted" /><input className="field-input pl-10" value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Buscar nome, e-mail ou telefone" /></label><div className="flex gap-2"><button className="secondary-button flex-1 justify-center md:hidden" type="button" onClick={() => setMobileOpen(true)}><Filter className="size-4" />Filtros{activeCount > 0 ? ` (${activeCount})` : ''}</button><button className="secondary-button justify-center" type="button" onClick={onClear}><X className="size-4" />Limpar filtros</button></div></div>
    <div className="mt-3 hidden grid-cols-2 gap-3 md:grid lg:grid-cols-5"><FilterControls filters={filters} onChange={onChange} /></div>
    {activeCount > 0 && <p className="mt-3 text-sm text-muted" role="status">{activeCount} filtro{activeCount === 1 ? '' : 's'} ativo{activeCount === 1 ? '' : 's'}</p>}
    {mobileOpen && <Dialog title="Filtros de leads" onClose={() => setMobileOpen(false)}><div className="grid gap-4"><FilterControls filters={filters} onChange={onChange} /></div><div className="mt-6 flex justify-between gap-3"><button className="secondary-button" type="button" onClick={() => { onClear(); setMobileOpen(false) }}><X className="size-4" />Limpar</button><button className="primary-button w-auto" type="button" onClick={() => setMobileOpen(false)}>Concluir</button></div></Dialog>}
  </section>
}
