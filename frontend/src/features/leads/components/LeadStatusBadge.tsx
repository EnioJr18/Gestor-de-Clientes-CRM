import { statusLabels } from '../utils/leadFormatters'
import type { LeadStatus } from '../types/lead'
export function LeadStatusBadge({ status }: { status: LeadStatus }) { return <span className="badge badge-status" aria-label={`Status: ${statusLabels[status]}`}>{statusLabels[status]}</span> }
