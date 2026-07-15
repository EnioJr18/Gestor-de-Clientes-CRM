import axios from 'axios'

import { appConfig } from '../../app/config/env'

export const publicClient = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: 10_000,
  withCredentials: true,
  headers: { Accept: 'application/json' },
})
