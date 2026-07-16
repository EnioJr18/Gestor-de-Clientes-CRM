import { lazy, Suspense } from 'react'
import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '../../features/auth/components/ProtectedRoute'
import { PublicRoute } from '../../features/auth/components/PublicRoute'
import { AppLayout } from '../../components/layout/AppLayout'
const DashboardPage = lazy(() => import('../../features/dashboard/pages/DashboardPage').then((module) => ({ default: module.DashboardPage })))
const LeadsPage = lazy(() => import('../../features/leads/pages/LeadsPage').then((module) => ({ default: module.LeadsPage })))
const LeadDetailsPage = lazy(() => import('../../features/leads/pages/LeadDetailsPage').then((module) => ({ default: module.LeadDetailsPage })))
const LoginPage = lazy(() => import('../../features/auth/pages/LoginPage').then((module) => ({ default: module.LoginPage })))
const NotFoundPage = lazy(() => import('./NotFoundPage').then((module) => ({ default: module.NotFoundPage })))
const fallback = <main className="grid min-h-screen place-items-center bg-canvas p-6" role="status">Carregando pagina...</main>

export function AppRoutes() {
  return (
    <Suspense fallback={fallback}><Routes>
      <Route element={<PublicRoute />}><Route path="/login" element={<LoginPage />} /></Route>
      <Route element={<ProtectedRoute />}><Route element={<AppLayout />}><Route path="/app" element={<DashboardPage />} /><Route path="/app/leads" element={<LeadsPage />} /><Route path="/app/leads/:id" element={<LeadDetailsPage />} /></Route></Route>
      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes></Suspense>
  )
}
