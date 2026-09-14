import { LoaderCircle } from 'lucide-react'
import { Brand } from '../layout/Brand'

export function LoadingScreen() {
  return (
    <main className="grid min-h-screen place-items-center bg-canvas px-6" aria-busy="true">
      <div className="flex flex-col items-center gap-5 text-muted" role="status">
        <Brand showTagline={false} />
        <div className="flex items-center gap-3">
          <LoaderCircle className="size-5 animate-spin text-brand" aria-hidden="true" />
          <span>Preparando seu espaco de trabalho.</span>
        </div>
      </div>
    </main>
  )
}
