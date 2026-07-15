import { priorityLabels } from '../utils/leadFormatters'
import type { LeadPriority } from '../types/lead'
export function LeadPriorityBadge({ prioridade }: { prioridade: LeadPriority }) { return <span className="badge badge-priority" aria-label={`Prioridade: ${priorityLabels[prioridade]}`}>{priorityLabels[prioridade]}</span> }
