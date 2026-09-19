from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError, error_body

_HTTP_CODE_MAP = {
    401: "UNAUTHENTICATED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    409: "CONFLICT",
    429: "RATE_LIMITED",
}


def _json_error(
    status_code: int, code: str, message: str, details: Any = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=error_body(code, message, details),
    )


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return _json_error(exc.status_code, exc.code, exc.message, exc.details)


async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = [
        {
            "loc": list(error.get("loc", ())),
            "msg": error.get("msg"),
            "type": error.get("type"),
        }
        for error in exc.errors()
    ]
    return _json_error(422, "VALIDATION_ERROR", "Validation error", details)


async def http_exception_handler(
    _request: Request, exc: StarletteHTTPException
) -> JSONResponse:
    code = _HTTP_CODE_MAP.get(exc.status_code, "INTERNAL_ERROR")
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return _json_error(exc.status_code, code, message)


async def unhandled_exception_handler(
    _request: Request, _exc: Exception
) -> JSONResponse:
    return _json_error(500, "INTERNAL_ERROR", "Internal server error")


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
