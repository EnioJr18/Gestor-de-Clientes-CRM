import { zodResolver } from '@hookform/resolvers/zod'
import { KeyRound, Save, UserRound } from 'lucide-react'
import { cloneElement, useEffect, useState, type ReactElement } from 'react'
import { useMutation } from '@tanstack/react-query'
import { useForm, type UseFormRegisterReturn } from 'react-hook-form'
import { useNavigate } from 'react-router-dom'

import { normalizeApiError } from '../../../lib/errors/normalizeApiError'
import { changePasswordRequest, updateProfileRequest } from '../api/authApi'
import { useAuth } from '../hooks/useAuth'
import {
  changePasswordSchema,
  profileSchema,
  type ChangePasswordFormValues,
  type ProfileFormValues,
} from '../schemas/accountSchemas'

const emptyProfile: ProfileFormValues = { username: '', email: '', first_name: '', last_name: '' }

export function ProfilePage() {
  const { user, updateUser, endSession } = useAuth()
  const navigate = useNavigate()
  const [profileSuccess, setProfileSuccess] = useState<string | null>(null)
  const profileForm = useForm<ProfileFormValues>({ resolver: zodResolver(profileSchema), defaultValues: emptyProfile })
  const passwordForm = useForm<ChangePasswordFormValues>({ resolver: zodResolver(changePasswordSchema) })
  const profileMutation = useMutation({ mutationFn: updateProfileRequest })
  const passwordMutation = useMutation({
    mutationFn: changePasswordRequest,
    onSuccess: () => {
      endSession('Senha alterada com sucesso. Entre novamente para continuar.')
      navigate('/login', { replace: true })
    },
  })

  useEffect(() => {
    if (user) profileForm.reset(user)
  }, [profileForm, user])

  const profileApiError = profileMutation.error ? normalizeApiError(profileMutation.error) : null
  const passwordApiError = passwordMutation.error ? normalizeApiError(passwordMutation.error) : null
  const profileError = (field: keyof ProfileFormValues) => profileForm.formState.errors[field]?.message || profileApiError?.errors?.[field]?.[0]
  const passwordError = (field: keyof ChangePasswordFormValues) => passwordForm.formState.errors[field]?.message || passwordApiError?.errors?.[field]?.[0]
  const saveProfile = profileForm.handleSubmit((values) => {
    setProfileSuccess(null)
    profileMutation.mutate(values, {
      onSuccess: (updatedUser) => {
        updateUser(updatedUser)
        profileForm.reset(updatedUser)
        setProfileSuccess('Dados da conta atualizados.')
      },
    })
  })
  const changePassword = passwordForm.handleSubmit((values) => passwordMutation.mutate(values))

  return (
    <section className="max-w-3xl">
      <header className="mb-8">
        <p className="text-sm font-medium text-brand">Conta</p>
        <h1 className="mt-1 text-3xl font-semibold text-strong">Meu perfil</h1>
        <p className="mt-2 text-muted">Mantenha seus dados e sua senha atualizados.</p>
      </header>

      <section className="state-card" aria-labelledby="profile-details-title" aria-busy={profileMutation.isPending}>
        <div className="flex items-start gap-3"><UserRound className="mt-1 size-5 text-brand" aria-hidden="true" /><div><h2 id="profile-details-title" className="text-xl font-semibold text-strong">Dados da conta</h2><p className="mt-1 text-sm text-muted">Estas informacoes aparecem na sua area de trabalho.</p></div></div>
        <form className="mt-6 space-y-5" onSubmit={saveProfile} noValidate>
          <div className="grid gap-5 sm:grid-cols-2">
            <ProfileField id="profile-first-name" label="Nome" error={profileError('first_name')} input={<input id="profile-first-name" autoComplete="given-name" className="field-input" {...profileForm.register('first_name')} />} />
            <ProfileField id="profile-last-name" label="Sobrenome" error={profileError('last_name')} input={<input id="profile-last-name" autoComplete="family-name" className="field-input" {...profileForm.register('last_name')} />} />
          </div>
          <ProfileField id="profile-username" label="Nome de usuario" error={profileError('username')} input={<input id="profile-username" autoComplete="username" className="field-input" {...profileForm.register('username')} />} />
          <ProfileField id="profile-email" label="E-mail" error={profileError('email')} input={<input id="profile-email" type="email" autoComplete="email" className="field-input" {...profileForm.register('email')} />} />
          {profileApiError && !profileApiError.errors && <p className="field-error" role="alert">{profileApiError.message}</p>}
          {profileSuccess && <p className="rounded-xl bg-success/15 px-4 py-3 text-sm text-success" role="status" aria-live="polite">{profileSuccess}</p>}
          <div className="flex justify-end"><button className="primary-button w-auto" type="submit" disabled={profileMutation.isPending}><Save className="size-4" aria-hidden="true" />{profileMutation.isPending ? 'Salvando...' : 'Salvar dados'}</button></div>
        </form>
      </section>

      <section className="state-card mt-6" aria-labelledby="profile-security-title" aria-busy={passwordMutation.isPending}>
        <div className="flex items-start gap-3"><KeyRound className="mt-1 size-5 text-brand" aria-hidden="true" /><div><h2 id="profile-security-title" className="text-xl font-semibold text-strong">Seguranca</h2><p className="mt-1 text-sm text-muted">Ao alterar sua senha, voce precisara entrar novamente.</p></div></div>
        <form className="mt-6 space-y-5" onSubmit={changePassword} noValidate>
          <PasswordField id="current-password" label="Senha atual" error={passwordError('current_password')} register={passwordForm.register('current_password')} autoComplete="current-password" />
          <PasswordField id="new-password" label="Nova senha" error={passwordError('new_password')} register={passwordForm.register('new_password')} autoComplete="new-password" />
          <PasswordField id="new-password-confirm" label="Confirmar nova senha" error={passwordError('new_password_confirm')} register={passwordForm.register('new_password_confirm')} autoComplete="new-password" />
          {passwordApiError && !passwordApiError.errors && <p className="field-error" role="alert">{passwordApiError.message}</p>}
          <div className="flex justify-end"><button className="primary-button w-auto" type="submit" disabled={passwordMutation.isPending}><KeyRound className="size-4" aria-hidden="true" />{passwordMutation.isPending ? 'Alterando...' : 'Alterar senha'}</button></div>
        </form>
      </section>
    </section>
  )
}

function ProfileField({ id, label, error, input }: { id: string; label: string; error?: string; input: ReactElement<{ 'aria-invalid'?: boolean; 'aria-describedby'?: string }> }) {
  return <div><label className="field-label" htmlFor={id}>{label}</label>{cloneElement(input, { 'aria-invalid': Boolean(error), 'aria-describedby': error ? `${id}-error` : undefined })}{error && <p id={`${id}-error`} className="field-error" role="alert">{error}</p>}</div>
}

function PasswordField({ id, label, error, register, autoComplete }: { id: string; label: string; error?: string; register: UseFormRegisterReturn; autoComplete: string }) {
  return <div><label className="field-label" htmlFor={id}>{label}</label><input id={id} type="password" autoComplete={autoComplete} className="field-input" aria-invalid={Boolean(error)} aria-describedby={error ? `${id}-error` : undefined} {...register} />{error && <p id={`${id}-error`} className="field-error" role="alert">{error}</p>}</div>
}
