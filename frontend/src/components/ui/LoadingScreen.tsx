import { LoaderCircle } from 'lucide-react'

export function LoadingScreen() {
  return (
    <main className="grid min-h-screen place-items-center bg-canvas px-6" aria-busy="true">
      <div className="flex items-center gap-3 text-muted" role="status">
        <LoaderCircle className="size-5 animate-spin" aria-hidden="true" />
        <span>Validando sua sessao...</span>
      </div>
    </main>
  )
}
