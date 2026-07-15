import { z } from 'zod'

export const userSchema = z.object({
  id: z.number().int().positive(),
  username: z.string(),
  first_name: z.string(),
  last_name: z.string(),
  email: z.string(),
})

const accessResponseFields = {
  access: z.string().min(1),
  token_type: z.literal('Bearer'),
  expires_in: z.number().int().positive(),
}

export const loginResponseSchema = z.object({
  ...accessResponseFields,
  user: userSchema,
})

export const refreshResponseSchema = z.object(accessResponseFields)
export const csrfResponseSchema = z.object({ csrfToken: z.string().min(1) })

export const apiErrorSchema = z.object({
  status: z.number().int(),
  code: z.string(),
  message: z.string(),
  errors: z.record(z.string(), z.array(z.string())).nullable(),
})

export type User = z.infer<typeof userSchema>
export type LoginResponse = z.infer<typeof loginResponseSchema>
export type RefreshResponse = z.infer<typeof refreshResponseSchema>
export type ApiError = z.infer<typeof apiErrorSchema>

export type LoginPayload = {
  username: string
  password: string
}

export type AuthStatus =
  | 'idle'
  | 'loading'
  | 'authenticated'
  | 'unauthenticated'
  | 'error'
