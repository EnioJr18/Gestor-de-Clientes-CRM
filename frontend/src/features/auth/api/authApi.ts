import {
  loginResponseSchema,
  userSchema,
  type LoginPayload,
  type LoginResponse,
  type User,
} from '../types/auth'
import { apiClient } from '../../../lib/api/client'
import { ensureCsrfToken } from '../../../lib/api/csrf'
import { publicClient } from '../../../lib/api/transport'

export async function loginRequest(payload: LoginPayload): Promise<LoginResponse> {
  const response = await publicClient.post('/auth/login/', payload)
  return loginResponseSchema.parse(response.data)
}

export async function currentUserRequest(): Promise<User> {
  const response = await apiClient.get('/users/me/')
  return userSchema.parse(response.data)
}

export async function logoutRequest(): Promise<void> {
  const csrfToken = await ensureCsrfToken()
  await publicClient.post('/auth/logout/', {}, { headers: { 'X-CSRFToken': csrfToken } })
}
