export const chartColors = {
  brand: '#8b6cff',
  brandHover: '#a896ff',
  canvas: '#121a30',
  grid: '#2a3655',
  muted: '#b5c0d7',
  strong: '#f2f5ff',
}

export const chartDistributionColors = ['#3157d5', '#6076d9', '#94a3e8', '#e5b65a', '#a32222']

export function chartAnimation(reduced: boolean) { return reduced ? false : { duration: 800, easing: 'easeOutQuart' as const } }

export const chartTooltip = { backgroundColor: chartColors.canvas, titleColor: chartColors.strong, bodyColor: chartColors.strong }

export const chartBarScales = {
  y: { beginAtZero: true, ticks: { precision: 0, color: chartColors.muted }, grid: { color: chartColors.grid } },
  x: { ticks: { color: chartColors.muted }, grid: { display: false } },
}
