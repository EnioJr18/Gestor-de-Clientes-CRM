import { z } from 'zod'

const requiredText = (message: string) => z.string().trim().min(1, message)
const password = z.string().min(8, 'A senha deve ter pelo menos 8 caracteres.')

export const registrationSchema = z
  .object({
    username: requiredText('Informe seu nome de usuario.'),
    email: z.string().trim().email('Informe um e-mail valido.'),
    first_name: requiredText('Informe seu nome.'),
    last_name: requiredText('Informe seu sobrenome.'),
    password,
    password_confirm: password,
  })
  .refine((values) => values.password === values.password_confirm, {
    message: 'As senhas devem coincidir.',
    path: ['password_confirm'],
  })

export type RegistrationFormValues = z.infer<typeof registrationSchema>

export const profileSchema = z.object({
  username: requiredText('Informe seu nome de usuario.'),
  email: z.string().trim().email('Informe um e-mail valido.'),
  first_name: requiredText('Informe seu nome.'),
  last_name: requiredText('Informe seu sobrenome.'),
})

export type ProfileFormValues = z.infer<typeof profileSchema>

export const changePasswordSchema = z
  .object({
    current_password: z.string().min(1, 'Informe sua senha atual.'),
    new_password: password,
    new_password_confirm: password,
  })
  .refine((values) => values.new_password === values.new_password_confirm, {
    message: 'As senhas devem coincidir.',
    path: ['new_password_confirm'],
  })

export type ChangePasswordFormValues = z.infer<typeof changePasswordSchema>
