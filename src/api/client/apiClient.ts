import { API_PATHS } from '@/api/contracts/paths';
import { publicRuntimeConfig } from '@/app/config/appConfig';

export type ApiRequestOptions = {
  method: 'GET' | 'POST';
  body?: unknown;
  correlationId?: string;
  signal?: AbortSignal;
};

/**
 * Same-origin JSON client. Provider SDKs stay server-side.
 */
export async function apiRequest<T>(path: string, options: ApiRequestOptions): Promise<T> {
  const url = path.startsWith('http')
    ? path
    : `${publicRuntimeConfig.apiBaseUrl.replace(/\/api\/v1$/, '')}${path}`;
  const init: RequestInit = {
    method: options.method,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      'X-Request-Id': options.correlationId ?? crypto.randomUUID(),
    },
  };
  if (options.body !== undefined) {
    init.body = JSON.stringify(options.body);
  }
  if (options.signal) {
    init.signal = options.signal;
  }
  const response = await fetch(url, init);

  if (!response.ok) {
    throw new Error(`API_ERROR_${response.status}`);
  }

  return (await response.json()) as T;
}

export { API_PATHS };
