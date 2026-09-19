export type ApiErrorShape = {
  error: {
    code: string;
    message: string;
    details: unknown;
  };
};

export class ApiError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details: unknown;

  constructor(status: number, code: string, message: string, details: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function isApiErrorShape(value: unknown): value is ApiErrorShape {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const error = (value as { error?: unknown }).error;
  if (typeof error !== "object" || error === null) {
    return false;
  }
  const record = error as { code?: unknown; message?: unknown };
  return typeof record.code === "string" && typeof record.message === "string";
}

export function normalizeApiError(status: number, body: unknown): ApiError {
  if (isApiErrorShape(body)) {
    return new ApiError(status, body.error.code, body.error.message, body.error.details ?? null);
  }
  return new ApiError(
    status,
    status === 401 ? "UNAUTHENTICATED" : "INTERNAL_ERROR",
    status === 401 ? "Unauthenticated" : "Request failed",
    body,
  );
}

export function errorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return error.message;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return "Something went wrong";
}
