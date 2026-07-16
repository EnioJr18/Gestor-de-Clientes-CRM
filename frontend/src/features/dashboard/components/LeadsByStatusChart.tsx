import { Doughnut } from 'react-chartjs-2'
import { ArcElement, Chart as ChartJS, Legend, Tooltip } from 'chart.js'
import type { DashboardStatusItem } from '../types/dashboard'
ChartJS.register(ArcElement, Tooltip, Legend)
const colors = ['#3157d5', '#6076d9', '#94a3e8', '#e5b65a', '#a32222']
export function LeadsByStatusChart({ items }: { items: DashboardStatusItem[] }) { return <article className="lead-card"><h2 className="text-lg font-semibold text-strong">Leads por status</h2><p className="mt-1 text-sm text-muted">Distribuicao atual dos seus leads.</p><div className="mt-5 h-72"><Doughnut aria-label="Grafico de leads por status" data={{ labels: items.map((item) => item.label), datasets: [{ data: items.map((item) => item.count), backgroundColor: colors }] }} options={{ responsive: true, maintainAspectRatio: false }} /></div><ul className="mt-4 grid gap-2 text-sm text-muted">{items.map((item) => <li key={item.status}><strong className="text-strong">{item.label}:</strong> {item.count}</li>)}</ul></article> }
