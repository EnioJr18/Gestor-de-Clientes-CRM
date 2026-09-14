import { CrmProMark } from '../brand/CrmProMark'

type BrandProps = {
  className?: string
  showTagline?: boolean
}

export function Brand({ className = '', showTagline = true }: BrandProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`.trim()}>
      <CrmProMark className="size-10 shrink-0" />
      <div>
        <p className="font-semibold tracking-tight text-strong">CRM.Pro</p>
        {showTagline ? <p className="text-xs text-muted">Relacionamentos com clareza</p> : null}
      </div>
    </div>
  )
}
