import { AxiosError, AxiosHeaders } from 'axios'
import { ZodError, z } from 'zod'

import { normalizeApiError } from './normalizeApiError'

function responseError(status: number, data: unknown) {
  return new AxiosError('request failed', 'ERR_BAD_REQUEST', undefined, undefined, {
    status,
    statusText: 'Error',
    data,
    headers: {},
    config: { headers: new AxiosHeaders() },
  })
}

describe('normalizeApiError', () => {
  it('preserva o contrato padronizado do backend', () => {
    const error = responseError(429, {
      status: 429,
      code: 'throttled',
      message: 'Muitas requisicoes.',
      errors: null,
    })
    expect(normalizeApiError(error)).toMatchObject({ status: 429, code: 'throttled' })
  })

  it.each([
    [new AxiosError('timeout', 'ECONNABORTED'), 'timeout'],
    [new AxiosError('network'), 'network_error'],
    [responseError(401, '<html>'), 'authentication_failed'],
    [responseError(403, {}), 'unexpected_response'],
  ])('normaliza timeout, rede e respostas inesperadas', (error, code) => {
    expect(normalizeApiError(error).code).toBe(code)
  })

  it('trata payload critico invalido sem stack trace', () => {
    let zodError: ZodError | null = null
    try {
      z.string().parse(1)
    } catch (error: unknown) {
      if (error instanceof ZodError) zodError = error
    }
    expect(normalizeApiError(zodError).code).toBe('invalid_response')
  })
})
