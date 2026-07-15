import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { LoadingScreen } from '../../../components/ui/LoadingScreen'
import { useAuth } from '../hooks/useAuth'

export function ProtectedRoute() {
  const { status } = useAuth()
  const location = useLocation()

  if (status === 'idle' || status === 'loading') return <LoadingScreen />
  if (status !== 'authenticated') {
    const from = `${location.pathname}${location.search}${location.hash}`
    return <Navigate to="/login" replace state={{ from }} />
  }
  return <Outlet />
}
