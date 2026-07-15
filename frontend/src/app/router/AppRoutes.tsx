import { Navigate, Route, Routes } from 'react-router-dom'

import { ProtectedRoute } from '../../features/auth/components/ProtectedRoute'
import { PublicRoute } from '../../features/auth/components/PublicRoute'
import { AuthenticatedHomePage } from '../../features/auth/pages/AuthenticatedHomePage'
import { LoginPage } from '../../features/auth/pages/LoginPage'
import { NotFoundPage } from './NotFoundPage'

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<PublicRoute />}><Route path="/login" element={<LoginPage />} /></Route>
      <Route element={<ProtectedRoute />}><Route path="/app" element={<AuthenticatedHomePage />} /></Route>
      <Route path="/" element={<Navigate to="/app" replace />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  )
}
