import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js'
import { Doughnut } from 'react-chartjs-2'
import { usePrefersReducedMotion } from '../../../lib/hooks/usePrefersReducedMotion'
import type { DashboardInteractionTypeItem } from '../types/dashboard'
import { interactionTypeLabel } from '../utils/dashboardFormatters'
import { chartAnimation, chartDistributionColors, chartTooltip } from '../utils/chartTheme'

ChartJS.register(ArcElement, Tooltip, Legend)

export function InteractionsByTypeChart({ items }: { items: DashboardInteractionTypeItem[] }) {
  const reduced = usePrefersReducedMotion()
  const labels = items.map((item) => interactionTypeLabel(item.tipo))
  return <article className="lead-card"><h2 className="text-lg font-semibold text-strong">Interacoes por tipo</h2><p className="mt-1 text-sm text-muted">Distribuicao dos contatos no periodo.</p><div className="mt-5 h-72"><Doughnut aria-label="Grafico de interacoes por tipo" data={{ labels, datasets: [{ data: items.map((item) => item.count), backgroundColor: chartDistributionColors }] }} options={{ responsive: true, maintainAspectRatio: false, animation: chartAnimation(reduced), plugins: { tooltip: chartTooltip } }} /></div><ul className="mt-4 grid gap-2 text-sm text-muted">{items.map((item) => <li key={item.tipo}><strong className="text-strong">{interactionTypeLabel(item.tipo)}:</strong> {item.count}</li>)}</ul></article>
}
