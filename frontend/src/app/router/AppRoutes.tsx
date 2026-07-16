import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '../../features/auth/components/ProtectedRoute'
import { PublicRoute } from '../../features/auth/components/PublicRoute'
import { DashboardPage } from '../../features/dashboard/pages/DashboardPage'
import { AppLayout } from '../../components/layout/AppLayout'
import { LeadDetailsPage } from '../../features/leads/pages/LeadDetailsPage'
import { LeadsPage } from '../../features/leads/pages/LeadsPage'
import { LoginPage } from '../../features/auth/pages/LoginPage'
import { NotFoundPage } from './NotFoundPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}><Route path="/login" element={<LoginPage />} /></Route>
      <Route element={<ProtectedRoute />}><Route element={<AppLayout />}><Route path="/app" element={<DashboardPage />} /><Route path="/app/leads" element={<LeadsPage />} /><Route path="/app/leads/:id" element={<LeadDetailsPage />} /></Route></Route>
      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
