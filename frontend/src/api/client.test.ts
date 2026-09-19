import { createApiClient } from "./client";
import { ApiError } from "../lib/errors";

function jsonResponse(status: number, body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

describe("API client", () => {
  it("attaches the bearer token", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(jsonResponse(200, { status: "ok" }));
    const client = createApiClient({
      getToken: () => "abc",
      fetchImpl,
    });

    await client.request("/health");

    expect(fetchImpl).toHaveBeenCalledTimes(1);
    const [, init] = fetchImpl.mock.calls[0] as [string, RequestInit];
    expect(new Headers(init.headers).get("Authorization")).toBe("Bearer abc");
  });

  it("normalizes the standard error envelope", async () => {
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse(403, { error: { code: "FORBIDDEN", message: "No access", details: null } }),
    );
    const client = createApiClient({ getToken: () => null, fetchImpl });

    await expect(client.request("/secret")).rejects.toMatchObject({
      name: "ApiError",
      status: 403,
      code: "FORBIDDEN",
      message: "No access",
    } satisfies Partial<ApiError>);
  });

  it("appends as_of from getAsOf when the path has none", async () => {
    const fetchImpl = vi
      .fn()
      .mockResolvedValueOnce(jsonResponse(200, { status: "ok" }))
      .mockResolvedValueOnce(jsonResponse(200, { status: "ok" }));
    const client = createApiClient({
      getToken: () => null,
      getAsOf: () => "2026-10-17",
      fetchImpl,
    });

    await client.request("/students/me/overview");
    await client.request("/risk/me?refresh=1");

    expect(fetchImpl.mock.calls[0]?.[0]).toBe("/api/v1/students/me/overview?as_of=2026-10-17");
    expect(fetchImpl.mock.calls[1]?.[0]).toBe("/api/v1/risk/me?refresh=1&as_of=2026-10-17");
  });

  it("clears session on 401", async () => {
    const onUnauthorized = vi.fn();
    const fetchImpl = vi.fn().mockResolvedValue(
      jsonResponse(401, {
        error: { code: "UNAUTHENTICATED", message: "Unauthenticated", details: null },
      }),
    );
    const client = createApiClient({
      getToken: () => "expired",
      onUnauthorized,
      fetchImpl,
    });

    await expect(client.request("/auth/me")).rejects.toBeInstanceOf(ApiError);
    expect(onUnauthorized).toHaveBeenCalledTimes(1);
  });
});
