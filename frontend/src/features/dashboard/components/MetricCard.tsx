import type { LucideIcon } from 'lucide-react'
type MetricCardProps = { title: string; value: string; description: string; icon: LucideIcon }
export function MetricCard({ title, value, description, icon: Icon }: MetricCardProps) { return <article className="lead-card"><div className="flex items-start justify-between gap-3"><div><p className="text-sm font-medium text-muted">{title}</p><p className="mt-2 text-3xl font-semibold text-strong">{value}</p></div><Icon className="size-5 text-brand" aria-hidden="true" /></div><p className="mt-3 text-sm text-muted">{description}</p></article> }
