import { ChartNoAxesCombined, Users } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

export function AuthenticatedHomePage() {
  const { user } = useAuth()

  return (
    <section>
        <p className="text-sm font-medium text-brand">Sessao autenticada</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight text-strong">Ola, {user?.first_name || user?.username}.</h1>
        <p className="mt-3 text-muted">Dashboard sera construido em uma proxima etapa.</p>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          <article className="placeholder-card"><Users className="size-6 text-brand" aria-hidden="true" /><h2 className="mt-5 text-xl font-semibold text-strong">Leads</h2><p className="mt-2 text-muted">O fluxo visual de leads entra na proxima etapa.</p></article>
          <article className="placeholder-card"><ChartNoAxesCombined className="size-6 text-brand" aria-hidden="true" /><h2 className="mt-5 text-xl font-semibold text-strong">Dashboard</h2><p className="mt-2 text-muted">Metricas e graficos permanecem fora desta sprint.</p></article>
        </div>
    </section>
  )
}
