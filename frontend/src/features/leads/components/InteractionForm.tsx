import { zodResolver } from '@hookform/resolvers/zod'
import { format } from 'date-fns'
import { useEffect } from 'react'
import { useForm } from 'react-hook-form'

import type { ApiError } from '../../auth/types/auth'
import { interactionFormSchema, toInteractionPayload, type InteractionFormValues } from '../schemas/interactionSchema'
import { interactionTypes, type Interaction } from '../types/interaction'
import { interactionPresentation, toDateTimeLocalValue } from '../utils/interactionFormatters'

const defaults: InteractionFormValues = {
  tipo: 'NOTA',
  dataInteracao: format(new Date(), "yyyy-MM-dd'T'HH:mm"),
  nota: '',
}

export function InteractionForm({ interaction, submitting, error, onSubmit, onCancel }: { interaction?: Interaction; submitting: boolean; error: ApiError | null; onSubmit: (values: ReturnType<typeof toInteractionPayload>) => void; onCancel: () => void }) {
  const { register, handleSubmit, formState: { errors }, reset } = useForm<InteractionFormValues>({ resolver: zodResolver(interactionFormSchema), defaultValues: defaults })

  useEffect(() => {
    reset(interaction ? {
      tipo: interaction.tipo,
      dataInteracao: toDateTimeLocalValue(interaction.data_interacao),
      nota: interaction.nota,
    } : { ...defaults, dataInteracao: format(new Date(), "yyyy-MM-dd'T'HH:mm") })
  }, [interaction, reset])

  const fieldError = (field: keyof InteractionFormValues) => errors[field]?.message || error?.errors?.[field]?.[0]

  return <form className="space-y-4" onSubmit={handleSubmit((values) => onSubmit(toInteractionPayload(values)))} noValidate>
    <div className="grid gap-4 sm:grid-cols-2">
      <Field label="Tipo" error={fieldError('tipo')}>
        <select className="field-input" {...register('tipo')} autoFocus>
          {interactionTypes.map((type) => <option key={type} value={type}>{interactionPresentation[type].label}</option>)}
        </select>
      </Field>
      <Field label="Data e hora" error={fieldError('dataInteracao')}>
        <input className="field-input" type="datetime-local" {...register('dataInteracao')} />
      </Field>
    </div>
    <Field label="Observacao" error={fieldError('nota')}>
      <textarea className="field-input min-h-28 resize-y" {...register('nota')} />
    </Field>
    {error && !error.errors && <p className="field-error" role="alert">{error.message}</p>}
    <div className="flex flex-wrap justify-end gap-3">
      <button className="secondary-button" type="button" disabled={submitting} onClick={onCancel}>Cancelar</button>
      <button className="primary-button w-auto" type="submit" disabled={submitting}>{submitting ? 'Salvando...' : interaction ? 'Salvar alteracoes' : 'Registrar interacao'}</button>
    </div>
  </form>
}

function Field({ label, error, children }: { label: string; error?: string; children: React.ReactNode }) {
  return <label><span className="field-label">{label}</span>{children}{error && <span className="field-error" role="alert">{error}</span>}</label>
}
