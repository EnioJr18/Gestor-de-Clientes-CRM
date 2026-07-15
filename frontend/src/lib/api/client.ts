import axios, { AxiosHeaders, type InternalAxiosRequestConfig } from 'axios'

import { appConfig } from '../../app/config/env'
import { refreshAccessToken } from './refresh'
import { clearAccessToken, getAccessToken } from './tokenStore'

declare module 'axios' {
  export interface AxiosRequestConfig {
    skipAuth?: boolean
    skipRefresh?: boolean
    retriedAfterRefresh?: boolean
  }
}

const authPaths = ['/auth/login/', '/auth/csrf/', '/auth/refresh/', '/auth/logout/']
let sessionExpiredHandler: (() => void) | null = null

function isAuthPath(url?: string): boolean {
  return authPaths.some((path) => url?.includes(path))
}

export function setSessionExpiredHandler(handler: (() => void) | null): void {
  sessionExpiredHandler = handler
}

export const apiClient = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 10_000,
  withCredentials: true,
  headers: { Accept: 'application/json' },
})

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = getAccessToken()
  const headers = AxiosHeaders.from(config.headers)
  if (token && !config.skipAuth && !isAuthPath(config.url) && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`)
  }
  config.headers = headers
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  async (error: unknown) => {
    if (!axios.isAxiosError(error) || !error.config) throw error

    const config = error.config
    const canRefresh =
      error.response?.status === 401 &&
      !config.skipRefresh &&
      !config.retriedAfterRefresh &&
      !isAuthPath(config.url)

    if (!canRefresh) throw error

    config.retriedAfterRefresh = true
    try {
      const token = await refreshAccessToken()
      const headers = AxiosHeaders.from(config.headers)
      headers.set('Authorization', `Bearer ${token}`)
      config.headers = headers
      return apiClient.request(config)
    } catch (refreshError: unknown) {
      clearAccessToken()
      sessionExpiredHandler?.()
      throw refreshError
    }
  },
)
