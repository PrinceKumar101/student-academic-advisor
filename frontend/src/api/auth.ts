import type { components } from "../types/api";
import type { createApiClient } from "./client";

export type TokenResponse = components["schemas"]["TokenResponse"];
export type MeResponse = components["schemas"]["MeResponse"];
export type RegisterRequest = components["schemas"]["RegisterRequest"];
export type RegisterResponse = components["schemas"]["RegisterResponse"];

export function loginRequest(
  client: ReturnType<typeof createApiClient>,
  username: string,
  password: string,
): Promise<TokenResponse> {
  const body = new URLSearchParams();
  body.set("username", username);
  body.set("password", password);
  return client.request<TokenResponse>("/auth/login", {
    method: "POST",
    skipAuth: true,
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
}

export function registerRequest(
  client: ReturnType<typeof createApiClient>,
  payload: RegisterRequest,
): Promise<RegisterResponse> {
  return client.request<RegisterResponse>("/auth/register", {
    method: "POST",
    skipAuth: true,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function meRequest(client: ReturnType<typeof createApiClient>): Promise<MeResponse> {
  return client.request<MeResponse>("/auth/me");
}

export function logoutRequest(client: ReturnType<typeof createApiClient>): Promise<void> {
  return client.request<void>("/auth/logout", { method: "POST" });
}
