import { zodResolver } from '@hookform/resolvers/zod'
import { ArrowRight, UserPlus } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'

import { Brand } from '../../../components/layout/Brand'
import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { registerRequest } from '../api/authApi'
import { registrationSchema, type RegistrationFormValues } from '../schemas/accountSchemas'

export function RegisterPage() {
  const navigate = useNavigate()
  const [submitError, setSubmitError] = useState<string | null>(null)
  const form = useForm<RegistrationFormValues>({ resolver: zodResolver(registrationSchema) })
  const registration = useMutation({
    mutationFn: registerRequest,
    onSuccess: () => {
      navigate('/login', {
        replace: true,
        state: { message: 'Conta criada com sucesso. Entre para continuar.' },
      })
    },
    onError: (error: unknown) => setSubmitError(normalizeApiError(error).message),
  })
  const apiError = registration.error ? normalizeApiError(registration.error) : null
  const fieldError = (field: keyof RegistrationFormValues) => form.formState.errors[field]?.message || apiError?.errors?.[field]?.[0]
  const submit = form.handleSubmit((values) => {
    setSubmitError(null)
    registration.mutate(values)
  })

  return (
    <main className="grid min-h-screen bg-canvas lg:grid-cols-[1.1fr_0.9fr]">
      <section className="hidden border-r border-line bg-panel p-12 lg:flex lg:flex-col lg:justify-between">
        <Brand />
        <div className="max-w-lg">
          <p className="mb-4 text-sm font-medium uppercase tracking-[0.18em] text-brand">CRM.Pro</p>
          <h1 className="text-5xl font-semibold leading-tight tracking-tight text-strong">Organize seus relacionamentos comerciais em um so lugar.</h1>
          <p className="mt-6 text-lg leading-8 text-muted">Acompanhe clientes, oportunidades e interacoes com mais clareza.</p>
        </div>
        <p className="text-sm text-muted">CRM.Pro</p>
      </section>

      <section className="flex items-center justify-center px-6 py-10 sm:px-10">
        <div className="w-full max-w-md">
          <div className="mb-8 lg:hidden"><Brand /></div>
          <div className="mb-8">
            <span className="mb-5 grid size-12 place-items-center rounded-2xl bg-brand-soft text-brand"><UserPlus className="size-5" aria-hidden="true" /></span>
            <h1 className="text-3xl font-semibold tracking-tight text-strong">Criar sua conta</h1>
            <p className="mt-2 text-muted">Comece a organizar seus relacionamentos comerciais.</p>
          </div>

          <form className="space-y-5" onSubmit={submit} noValidate aria-busy={registration.isPending}>
            <div>
              <label className="field-label" htmlFor="register-username">Nome de usuario</label>
              <input id="register-username" autoComplete="username" className="field-input" aria-invalid={Boolean(fieldError('username'))} aria-describedby={fieldError('username') ? 'register-username-error' : undefined} {...form.register('username')} />
              <FieldError id="register-username-error" message={fieldError('username')} />
            </div>
            <div>
              <label className="field-label" htmlFor="register-email">E-mail</label>
              <input id="register-email" type="email" autoComplete="email" className="field-input" aria-invalid={Boolean(fieldError('email'))} aria-describedby={fieldError('email') ? 'register-email-error' : undefined} {...form.register('email')} />
              <FieldError id="register-email-error" message={fieldError('email')} />
            </div>
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <label className="field-label" htmlFor="register-first-name">Nome</label>
                <input id="register-first-name" autoComplete="given-name" className="field-input" aria-invalid={Boolean(fieldError('first_name'))} aria-describedby={fieldError('first_name') ? 'register-first-name-error' : undefined} {...form.register('first_name')} />
                <FieldError id="register-first-name-error" message={fieldError('first_name')} />
              </div>
              <div>
                <label className="field-label" htmlFor="register-last-name">Sobrenome</label>
                <input id="register-last-name" autoComplete="family-name" className="field-input" aria-invalid={Boolean(fieldError('last_name'))} aria-describedby={fieldError('last_name') ? 'register-last-name-error' : undefined} {...form.register('last_name')} />
                <FieldError id="register-last-name-error" message={fieldError('last_name')} />
              </div>
            </div>
            <div>
              <label className="field-label" htmlFor="register-password">Senha</label>
              <input id="register-password" type="password" autoComplete="new-password" className="field-input" aria-invalid={Boolean(fieldError('password'))} aria-describedby={fieldError('password') ? 'register-password-error' : undefined} {...form.register('password')} />
              <FieldError id="register-password-error" message={fieldError('password')} />
            </div>
            <div>
              <label className="field-label" htmlFor="register-password-confirm">Confirmar senha</label>
              <input id="register-password-confirm" type="password" autoComplete="new-password" className="field-input" aria-invalid={Boolean(fieldError('password_confirm'))} aria-describedby={fieldError('password_confirm') ? 'register-password-confirm-error' : undefined} {...form.register('password_confirm')} />
              <FieldError id="register-password-confirm-error" message={fieldError('password_confirm')} />
            </div>
            {submitError && <p className="rounded-xl bg-danger-soft px-4 py-3 text-sm text-danger" role="alert">{submitError}</p>}
            <button className="primary-button" type="submit" disabled={registration.isPending}>
              <span>{registration.isPending ? 'Criando conta...' : 'Criar minha conta'}</span><ArrowRight className="size-4" aria-hidden="true" />
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-muted">Ja tenho uma conta? <Link className="font-medium text-brand underline-offset-4 hover:underline" to="/login">Entrar</Link></p>
        </div>
      </section>
    </main>
  )
}

function FieldError({ id, message }: { id: string; message?: string }) {
  return message ? <p id={id} className="field-error" role="alert">{message}</p> : null
}
