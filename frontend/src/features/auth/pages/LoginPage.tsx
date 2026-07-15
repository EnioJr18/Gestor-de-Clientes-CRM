import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, LockKeyhole } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { useLocation, useNavigate } from 'react-router-dom'

import { Brand } from '../../../components/layout/Brand'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { useAuth } from '../hooks/useAuth'
import { loginSchema, type LoginFormValues } from '../schemas/loginSchema'

function safeReturnPath(value: unknown): string {
  return typeof value === 'string' && value.startsWith('/') && !value.startsWith('//')
    ? value
    : '/app'
}

export function LoginPage() {
  const { login, errorMessage } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [submitError, setSubmitError] = useState<string | null>(errorMessage)
  const {
    register,
    handleSubmit,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({ resolver: zodResolver(loginSchema) })

  const submit = handleSubmit(async (values) => {
    setSubmitError(null)
    try {
      await login(values)
      const state = location.state as { from?: unknown } | null
      navigate(safeReturnPath(state?.from), { replace: true })
    } catch (error: unknown) {
      const normalized = normalizeApiError(error)
      if (normalized.errors?.username?.[0]) setError('username', { message: normalized.errors.username[0] })
      if (normalized.errors?.password?.[0]) setError('password', { message: normalized.errors.password[0] })
      setSubmitError(normalized.message)
    }
  })

  return (
    <main className="grid min-h-screen bg-canvas lg:grid-cols-[1.1fr_0.9fr]">
      <section className="hidden border-r border-line bg-panel p-12 lg:flex lg:flex-col lg:justify-between">
        <Brand />
        <div className="max-w-lg">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.18em] text-brand">Acesso seguro</p>
          <h1 className="text-5xl font-semibold leading-tight tracking-tight text-strong">Seu trabalho continua. Seus tokens nao.</h1>
          <p className="mt-6 text-lg leading-8 text-muted">O acesso permanece somente na memoria desta aba. A renovacao segura acontece por cookie HttpOnly.</p>
        </div>
        <p className="text-sm text-muted">Fundacao da SPA CRM.Pro</p>
      </section>

      <section className="flex items-center justify-center px-6 py-12 sm:px-10">
        <div className="w-full max-w-md">
          <div className="mb-10 lg:hidden"><Brand /></div>
          <div className="mb-8">
            <span className="mb-5 grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand"><LockKeyhole className="size-5" aria-hidden="true" /></span>
            <h2 className="text-3xl font-semibold tracking-tight text-strong">Entre na sua conta</h2>
            <p className="mt-2 text-muted">Use suas credenciais atuais do CRM.Pro.</p>
          </div>

          <form className="space-y-5" onSubmit={submit} noValidate>
            <div>
              <label className="field-label" htmlFor="username">Usuario</label>
              <input id="username" autoComplete="username" className="field-input" aria-invalid={Boolean(errors.username)} aria-describedby={errors.username ? 'username-error' : undefined} {...register('username')} />
              {errors.username && <p id="username-error" className="field-error">{errors.username.message}</p>}
            </div>
            <div>
              <label className="field-label" htmlFor="password">Senha</label>
              <input id="password" type="password" autoComplete="current-password" className="field-input" aria-invalid={Boolean(errors.password)} aria-describedby={errors.password ? 'password-error' : undefined} {...register('password')} />
              {errors.password && <p id="password-error" className="field-error">{errors.password.message}</p>}
            </div>
            {submitError && <p className="rounded-xl bg-danger-soft px-4 py-3 text-sm text-danger" role="alert">{submitError}</p>}
            <button className="primary-button" type="submit" disabled={isSubmitting}>
              <span>{isSubmitting ? 'Entrando...' : 'Entrar'}</span><ArrowRight className="size-4" aria-hidden="true" />
            </button>
          </form>
        </div>
      </section>
    </main>
  )
}
