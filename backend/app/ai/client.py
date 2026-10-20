
from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from app.core.config import Settings, get_settings
from app.core.logging import current_request_id

logger = logging.getLogger("app.ai")

REASON_NOT_CONFIGURED = "NOT_CONFIGURED"
REASON_TIMEOUT = "TIMEOUT"
REASON_PROVIDER_ERROR = "PROVIDER_ERROR"

GEMINI_BASE_URL = (
    "https://generativelanguage.googleapis.com/v1beta/openai/"
)


@dataclass(frozen=True)
class CompletionResult:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class AIClientError(Exception):
    def __init__(
        self,
        reason: str,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(message)
        self.reason = reason
        self.message = message
        self.retryable = retryable


class AIClient(Protocol):
    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        feature: str,
        timeout_seconds: int,
        max_tokens: int,
        user_id: int | None = None,
    ) -> CompletionResult: ...


class OpenAIClient:
    """Gemini client using Google's OpenAI-compatible API endpoint."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        sleep: Callable[[float], None] = time.sleep,
        sender: Callable[..., CompletionResult] | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._sleep = sleep
        self._sender = sender

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        feature: str,
        timeout_seconds: int,
        max_tokens: int,
        user_id: int | None = None,
    ) -> CompletionResult:
        if not self._settings.gemini_configured:
            raise AIClientError(
                REASON_NOT_CONFIGURED,
                "Gemini API key is not configured",
                retryable=False,
            )

        started = time.perf_counter()
        model = self._settings.gemini_model.strip()

        try:
            result = self._call(
                messages,
                timeout_seconds=timeout_seconds,
                max_tokens=max_tokens,
            )
        except AIClientError as exc:
            if not exc.retryable:
                self._log(
                    feature,
                    user_id,
                    started,
                    outcome=exc.reason,
                    model=model or None,
                )
                raise

            self._sleep(self._settings.ai_retry_backoff_seconds)

            try:
                result = self._call(
                    messages,
                    timeout_seconds=timeout_seconds,
                    max_tokens=max_tokens,
                )
            except AIClientError as retry_exc:
                self._log(
                    feature,
                    user_id,
                    started,
                    outcome=retry_exc.reason,
                    model=model or None,
                )
                raise

        self._log(
            feature,
            user_id,
            started,
            outcome="AI",
            model=result.model,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
        )
        return result

    def _call(
        self,
        messages: list[dict[str, str]],
        *,
        timeout_seconds: int,
        max_tokens: int,
    ) -> CompletionResult:
        if self._sender is not None:
            return self._sender(
                messages,
                timeout_seconds=timeout_seconds,
                max_tokens=max_tokens,
            )

        return self._send_gemini(
            messages,
            timeout_seconds=timeout_seconds,
            max_tokens=max_tokens,
        )

    def _send_gemini(
        self,
        messages: list[dict[str, str]],
        *,
        timeout_seconds: int,
        max_tokens: int,
    ) -> CompletionResult:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            OpenAI,
            RateLimitError,
        )

        model = (
            self._settings.gemini_model.strip()
            or "gemini-2.5-flash"
        )

        client = OpenAI(
            api_key=self._settings.gemini_api_key,
            base_url=GEMINI_BASE_URL,
            timeout=timeout_seconds,
        )

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.2,
                response_format={"type": "json_object"},
            )
        except APITimeoutError as exc:
            raise AIClientError(
                REASON_TIMEOUT,
                "Gemini API request timed out",
                retryable=True,
            ) from exc
        except RateLimitError as exc:
            raise AIClientError(
                REASON_PROVIDER_ERROR,
                "Gemini API rate-limited the request",
                retryable=True,
            ) from exc
        except APIConnectionError as exc:
            raise AIClientError(
                REASON_PROVIDER_ERROR,
                "Could not connect to the Gemini API",
                retryable=True,
            ) from exc
        except APIStatusError as exc:
            retryable = (
                exc.status_code >= 500
                or exc.status_code in (408, 429)
            )
            reason = (
                REASON_TIMEOUT
                if exc.status_code == 408
                else REASON_PROVIDER_ERROR
            )

            raise AIClientError(
                reason,
                f"Gemini API returned HTTP {exc.status_code}",
                retryable=retryable,
            ) from exc

        choice = (
            response.choices[0].message.content
            if response.choices
            else None
        )

        if not choice:
            raise AIClientError(
                REASON_PROVIDER_ERROR,
                "Gemini API returned an empty completion",
                retryable=False,
            )

        usage = response.usage

        return CompletionResult(
            text=choice,
            model=response.model or model,
            prompt_tokens=(
                usage.prompt_tokens if usage else None
            ),
            completion_tokens=(
                usage.completion_tokens if usage else None
            ),
        )

    def _log(
        self,
        feature: str,
        user_id: int | None,
        started: float,
        *,
        outcome: str,
        model: str | None,
        prompt_tokens: int | None = None,
        completion_tokens: int | None = None,
    ) -> None:
        logger.info(
            "ai_call",
            extra={
                "request_id": current_request_id(),
                "user_id": user_id,
                "feature": feature,
                "model": model,
                "latency_ms": round(
                    (time.perf_counter() - started) * 1000,
                    1,
                ),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "outcome": outcome,
            },
        )


class FakeAIClient:
    """Injectable stand-in. Tests never call the real provider."""

    def __init__(
        self,
        text: str = "{}",
        *,
        error: AIClientError | None = None,
        errors: list[AIClientError] | None = None,
        model: str = "fake",
    ) -> None:
        self.text = text
        self.error = error
        self.errors = list(errors or [])
        self.model = model
        self.calls = 0
        self.last_messages: list[dict[str, str]] | None = None

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        feature: str,
        timeout_seconds: int,
        max_tokens: int,
        user_id: int | None = None,
    ) -> CompletionResult:
        del feature, timeout_seconds, max_tokens, user_id

        self.calls += 1
        self.last_messages = messages

        if self.errors:
            raise self.errors.pop(0)

        if self.error is not None:
            raise self.error

        return CompletionResult(
            text=self.text,
            model=self.model,
        )


def get_ai_client() -> AIClient:
    return OpenAIClient()
