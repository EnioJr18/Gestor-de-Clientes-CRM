import { QueryClientProvider } from '@tanstack/react-query'
import { render } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'

import { AppRoutes } from '../app/router/AppRoutes'
import { AuthProvider } from '../features/auth/providers/AuthProvider'
import { createQueryClient } from '../lib/query/queryClient'

export function renderApp(initialPath = '/app') {
  const queryClient = createQueryClient()
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={[initialPath]}>
        <AuthProvider><AppRoutes /></AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )
}
