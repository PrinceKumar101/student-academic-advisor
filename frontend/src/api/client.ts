import { ApiError, normalizeApiError } from "../lib/errors";

export type ApiClientOptions = {
  baseUrl?: string;
  getToken: () => string | null;
  getAsOf?: () => string | null;
  onUnauthorized?: () => void;
  fetchImpl?: typeof fetch;
};

export type ApiRequestInit = RequestInit & {
  skipAuth?: boolean;
};

const API_PREFIX = "/api/v1";

export function withAsOf(path: string, asOf: string | null | undefined): string {
  if (!asOf) {
    return path;
  }
  if (/(?:^|[?&])as_of=/.test(path)) {
    return path;
  }
  return `${path}${path.includes("?") ? "&" : "?"}as_of=${encodeURIComponent(asOf)}`;
}

export function apiUrl(path: string, baseUrl = ""): string {
  const origin = baseUrl.replace(/\/$/, "");
  const suffix = path.startsWith("/") ? path : `/${path}`;
  return `${origin}${API_PREFIX}${suffix}`;
}

export function createApiClient(options: ApiClientOptions) {
  const fetchImpl = options.fetchImpl ?? fetch;
  const baseUrl = options.baseUrl ?? "";

  async function request<T>(path: string, init: ApiRequestInit = {}): Promise<T> {
    const headers = new Headers(init.headers);
    const token = options.getToken();
    if (token && !init.skipAuth && !headers.has("Authorization")) {
      headers.set("Authorization", `Bearer ${token}`);
    }

    const response = await fetchImpl(apiUrl(withAsOf(path, options.getAsOf?.()), baseUrl), {
      ...init,
      headers,
    });

    if (response.status === 204) {
      return undefined as T;
    }

    let body: unknown = null;
    const text = await response.text();
    if (text) {
      try {
        body = JSON.parse(text);
      } catch {
        body = text;
      }
    }

    if (response.status === 401) {
      options.onUnauthorized?.();
    }

    if (!response.ok) {
      throw normalizeApiError(response.status, body);
    }

    return body as T;
  }

  return { request };
}

export type ApiClient = ReturnType<typeof createApiClient>;

export { ApiError };
