import { QueryClient } from '@tanstack/react-query'
import axios from 'axios'

export function createQueryClient(): QueryClient {
  return new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 30_000,
        refetchOnWindowFocus: false,
        retry: (failureCount, error) =>
          failureCount < 2 && !(axios.isAxiosError(error) && error.response?.status === 401),
      },
      mutations: { retry: false },
    },
  })
}
