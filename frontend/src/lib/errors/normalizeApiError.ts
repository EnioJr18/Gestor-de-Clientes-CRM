import axios from 'axios'
import { ZodError } from 'zod'

import { apiErrorSchema, type ApiError } from '../../features/auth/types/auth'

const messages: Record<number, string> = {
  401: 'Sua sessao expirou. Entre novamente.',
  403: 'A requisicao de seguranca foi recusada. Tente novamente.',
  429: 'Muitas tentativas. Aguarde um momento antes de tentar novamente.',
  500: 'O servidor encontrou um problema. Tente novamente mais tarde.',
}

export function normalizeApiError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return { status: 0, code: 'timeout', message: 'A requisicao demorou demais.', errors: null }
    }

    if (!error.response) {
      return { status: 0, code: 'network_error', message: 'Nao foi possivel conectar ao servidor.', errors: null }
    }

    const parsed = apiErrorSchema.safeParse(error.response.data)
    if (parsed.success) {
      return parsed.data
    }

    const status = error.response.status
    return {
      status,
      code: status === 401 ? 'authentication_failed' : 'unexpected_response',
      message: messages[status] ?? 'Recebemos uma resposta inesperada do servidor.',
      errors: null,
    }
  }

  if (error instanceof ZodError) {
    return {
      status: 0,
      code: 'invalid_response',
      message: 'O servidor retornou dados em formato inesperado.',
      errors: null,
    }
  }

  return { status: 0, code: 'unknown_error', message: 'Nao foi possivel concluir a operacao.', errors: null }
}
