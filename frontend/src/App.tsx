import { BrowserRouter } from 'react-router-dom'

import { AppProviders } from './app/providers/AppProviders'
import { AppRoutes } from './app/router/AppRoutes'

export default function App() {
  return (
    <BrowserRouter>
      <AppProviders><AppRoutes /></AppProviders>
    </BrowserRouter>
  )
}
