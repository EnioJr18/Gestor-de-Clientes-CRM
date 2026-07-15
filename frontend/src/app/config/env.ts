import { z } from 'zod'

const apiUrlSchema = z
  .string({ error: 'VITE_API_BASE_URL e obrigatoria.' })
  .url('VITE_API_BASE_URL deve ser uma URL valida.')
  .transform((value) => value.replace(/\/$/, ''))
  .refine((value) => {
    const url = new URL(value)
    return ['http:', 'https:'].includes(url.protocol) && url.pathname.endsWith('/api/v1')
  }, 'VITE_API_BASE_URL deve usar HTTP(S) e terminar em /api/v1.')

export type AppConfig = {
  apiBaseUrl: string
}

export function loadAppConfig(env: { VITE_API_BASE_URL?: string }): AppConfig {
  return { apiBaseUrl: apiUrlSchema.parse(env.VITE_API_BASE_URL) }
}

export const appConfig = loadAppConfig({
  VITE_API_BASE_URL: import.meta.env.VITE_API_BASE_URL,
})
