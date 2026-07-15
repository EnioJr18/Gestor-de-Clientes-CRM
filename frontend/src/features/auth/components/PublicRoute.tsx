import { Navigate, Outlet } from 'react-router-dom'

import { LoadingScreen } from '../../../components/ui/LoadingScreen'
import { useAuth } from '../hooks/useAuth'

export function PublicRoute() {
  const { status } = useAuth()
  if (status === 'idle' || status === 'loading') return <LoadingScreen />
  if (status === 'authenticated') return <Navigate to="/app" replace />
  return <Outlet />
}
