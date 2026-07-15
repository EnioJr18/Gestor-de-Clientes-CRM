import { format } from 'date-fns'
import { ChartNoAxesCombined, LogOut, Users } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Brand } from '../../../components/layout/Brand'
import { useAuth } from '../hooks/useAuth'

export function AuthenticatedHomePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  async function handleLogout() {
    try {
      await logout()
    } finally {
      navigate('/login', { replace: true })
    }
  }

  return (
    <div className="min-h-screen bg-canvas">
      <header className="border-b border-line bg-panel">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Brand />
          <button className="secondary-button" type="button" onClick={() => void handleLogout()}><LogOut className="size-4" aria-hidden="true" />Sair</button>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-6 py-12">
        <p className="text-sm font-medium text-brand">Sessao autenticada</p>
        <h1 className="mt-2 text-4xl font-semibold tracking-tight text-strong">Ola, {user?.first_name || user?.username}.</h1>
        <p className="mt-3 text-muted">{format(new Date(), "'Sessao validada em' dd/MM/yyyy")}</p>
        <div className="mt-10 grid gap-5 md:grid-cols-2">
          <article className="placeholder-card"><Users className="size-6 text-brand" aria-hidden="true" /><h2 className="mt-5 text-xl font-semibold text-strong">Leads</h2><p className="mt-2 text-muted">O fluxo visual de leads entra na proxima etapa.</p></article>
          <article className="placeholder-card"><ChartNoAxesCombined className="size-6 text-brand" aria-hidden="true" /><h2 className="mt-5 text-xl font-semibold text-strong">Dashboard</h2><p className="mt-2 text-muted">Metricas e graficos permanecem fora desta sprint.</p></article>
        </div>
      </main>
    </div>
  )
}
