import { ShieldCheck } from 'lucide-react'

export function Brand() {
  return (
    <div className="flex items-center gap-3">
      <span className="grid size-10 place-items-center rounded-xl bg-brand text-white shadow-sm">
        <ShieldCheck className="size-5" aria-hidden="true" />
      </span>
      <div>
        <p className="font-semibold tracking-tight text-strong">CRM.Pro</p>
        <p className="text-xs text-muted">Relacionamentos com clareza</p>
      </div>
    </div>
  )
}
