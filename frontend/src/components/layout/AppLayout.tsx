import { ChartNoAxesCombined, LogOut, Menu, Users, X } from 'lucide-react'
import { useState } from 'react'
import { NavLink, Outlet, useNavigate } from 'react-router-dom'

import { useAuth } from '../../features/auth/hooks/useAuth'
import { Brand } from './Brand'

export function AppLayout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  async function leave() { try { await logout() } finally { navigate('/login', { replace: true }) } }
  const navigation = <nav className="space-y-1" aria-label="Navegacao principal"><NavLink to="/app" end className="nav-link"><ChartNoAxesCombined className="size-4" />Dashboard</NavLink><NavLink to="/app/leads" className="nav-link"><Users className="size-4" />Leads</NavLink></nav>
  return <div className="min-h-screen bg-canvas"><aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-line bg-panel p-5 md:block"><Brand /><div className="mt-10">{navigation}</div></aside><header className="sticky top-0 z-20 flex items-center justify-between border-b border-line bg-panel px-4 py-3 md:ml-64 md:px-8"><button type="button" className="secondary-button md:hidden" aria-label="Abrir navegacao" onClick={() => setOpen(true)}><Menu className="size-4" /></button><p className="hidden text-sm text-muted sm:block">{user?.first_name || user?.username}</p><button className="secondary-button" type="button" onClick={() => void leave()}><LogOut className="size-4" aria-hidden="true" />Sair</button></header>{open && <div className="fixed inset-0 z-40 bg-strong/30 md:hidden" role="presentation" onClick={() => setOpen(false)}><aside className="h-full w-72 bg-panel p-5" role="dialog" aria-label="Navegacao"><div className="flex items-center justify-between"><Brand /><button type="button" className="secondary-button" aria-label="Fechar navegacao" onClick={() => setOpen(false)}><X className="size-4" /></button></div><div className="mt-10" onClick={() => setOpen(false)}>{navigation}</div></aside></div>}<main className="mx-auto max-w-7xl p-4 md:ml-64 md:p-8"><Outlet /></main></div>
}
