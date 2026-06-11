import { API_BASE } from '@/lib/constants'
import type { ApiError } from '@/lib/types'

export class ApiRequestError extends Error {
  constructor(
    public readonly code: string,
    message: string,
  ) {
    super(message)
    this.name = 'ApiRequestError'
  }
}

async function fetchApi<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })

  if (!res.ok) {
    let error: ApiError = { code: 'UNKNOWN_ERROR', message: res.statusText }
    try {
      const body = await res.json()
      if (body?.error) error = body.error
    } catch {
      // response body not JSON — keep default error
    }
    throw new ApiRequestError(error.code, error.message)
  }

  return res.json() as Promise<T>
}

export const api = {
  get: <T>(path: string) => fetchApi<T>(path),

  post: <T>(path: string, body: unknown) =>
    fetchApi<T>(path, { method: 'POST', body: JSON.stringify(body) }),

  patch: <T>(path: string, body: unknown) =>
    fetchApi<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),

  delete: <T>(path: string) => fetchApi<T>(path, { method: 'DELETE' }),

  postForm: <T>(path: string, body: FormData) =>
    fetchApi<T>(path, {
      method: 'POST',
      body,
      headers: {},
    }),
}
