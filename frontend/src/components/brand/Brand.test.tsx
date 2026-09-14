import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { Brand } from '../layout/Brand'
import { LoadingScreen } from '../ui/LoadingScreen'

describe('identidade CRM.Pro', () => {
  it('exibe a marca sem referencias ao Vite', () => {
    const { container } = render(<Brand />)

    expect(screen.getByText('CRM.Pro')).toBeInTheDocument()
    expect(container.querySelector('svg[aria-hidden="true"]')).toBeInTheDocument()
    expect(screen.queryByText(/Vite/i)).not.toBeInTheDocument()
  })

  it('usa copy de produto no carregamento', () => {
    render(<LoadingScreen />)

    expect(screen.getByText('Preparando seu espaco de trabalho.')).toBeInTheDocument()
    expect(screen.queryByText('Validando sua sessao...')).not.toBeInTheDocument()
  })
})
