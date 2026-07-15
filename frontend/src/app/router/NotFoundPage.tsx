import { Link } from 'react-router-dom'

export function NotFoundPage() {
  return (
    <main className="grid min-h-screen place-items-center bg-canvas px-6 text-center">
      <div>
        <p className="text-sm font-medium text-brand">404</p>
        <h1 className="mt-2 text-3xl font-semibold text-strong">Pagina nao encontrada</h1>
        <Link className="mt-6 inline-block font-medium text-brand underline-offset-4 hover:underline" to="/app">Voltar ao CRM.Pro</Link>
      </div>
    </main>
  )
}
