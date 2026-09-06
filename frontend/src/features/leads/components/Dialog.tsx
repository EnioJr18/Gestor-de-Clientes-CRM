import { X } from 'lucide-react'
import { useEffect, useRef, type ReactNode } from 'react'
export function Dialog({ title, children, onClose, busy = false }: { title: string; children: ReactNode; onClose: () => void; busy?: boolean }) {
  const dialog = useRef<HTMLDivElement>(null); const previous = useRef<HTMLElement | null>(document.activeElement instanceof HTMLElement ? document.activeElement : null)
  useEffect(() => { const focused = previous.current; dialog.current?.focus(); const key = (event: KeyboardEvent) => { if (event.key === 'Escape' && !busy) onClose() }; document.addEventListener('keydown', key); return () => { document.removeEventListener('keydown', key); focused?.focus() } }, [busy, onClose])
  return <div className="dialog-backdrop" role="presentation" onMouseDown={busy ? undefined : onClose}><div ref={dialog} role="dialog" aria-modal="true" aria-labelledby="dialog-title" aria-busy={busy || undefined} tabIndex={-1} className="dialog-panel" onMouseDown={(event) => event.stopPropagation()}><div className="mb-5 flex items-center justify-between gap-4"><h2 id="dialog-title" className="text-xl font-semibold text-strong">{title}</h2><button type="button" className="secondary-button" aria-label="Fechar dialogo" disabled={busy} onClick={onClose}><X className="size-4" /></button></div>{children}</div></div>
}
