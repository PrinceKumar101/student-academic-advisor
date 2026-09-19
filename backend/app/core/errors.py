from typing import Any


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFound(AppError):
    def __init__(self, message: str = "Not found", details: Any = None) -> None:
        super().__init__("NOT_FOUND", message, 404, details)


class Forbidden(AppError):
    def __init__(self, message: str = "Forbidden", details: Any = None) -> None:
        super().__init__("FORBIDDEN", message, 403, details)


class Unauthenticated(AppError):
    def __init__(self, message: str = "Unauthenticated", details: Any = None) -> None:
        super().__init__("UNAUTHENTICATED", message, 401, details)


class Conflict(AppError):
    def __init__(self, message: str = "Conflict", details: Any = None) -> None:
        super().__init__("CONFLICT", message, 409, details)


class RateLimited(AppError):
    def __init__(self, message: str = "Rate limited", details: Any = None) -> None:
        super().__init__("RATE_LIMITED", message, 429, details)


def error_body(code: str, message: str, details: Any = None) -> dict[str, Any]:
    return {"error": {"code": code, "message": message, "details": details}}
