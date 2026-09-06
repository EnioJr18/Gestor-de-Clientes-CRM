import { BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Tooltip } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { usePrefersReducedMotion } from '../../../lib/hooks/usePrefersReducedMotion'
import type { DashboardInteractionEvolutionItem } from '../types/dashboard'
import { chartAnimation, chartBarScales, chartColors, chartTooltip } from '../utils/chartTheme'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

export function InteractionsEvolutionChart({ items }: { items: DashboardInteractionEvolutionItem[] }) {
  const reduced = usePrefersReducedMotion()
  return <article className="lead-card"><h2 className="text-lg font-semibold text-strong">Evolucao de interacoes</h2><p className="mt-1 text-sm text-muted">Contatos registrados em cada mes do periodo.</p><div className="mt-5 h-72"><Bar aria-label="Grafico de evolucao de interacoes" data={{ labels: items.map((item) => item.label), datasets: [{ label: 'Interacoes registradas', data: items.map((item) => item.count), backgroundColor: chartColors.brand, hoverBackgroundColor: chartColors.brandHover, borderRadius: 8 }] }} options={{ responsive: true, maintainAspectRatio: false, animation: chartAnimation(reduced), scales: chartBarScales, plugins: { tooltip: chartTooltip } }} /></div><dl className="sr-only">{items.map((item) => <div key={item.month}><dt>{item.label}</dt><dd>{item.count} interacoes registradas</dd></div>)}</dl></article>
}
