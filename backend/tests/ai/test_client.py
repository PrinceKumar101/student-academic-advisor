from app.ai.client import (
    REASON_PROVIDER_ERROR,
    REASON_TIMEOUT,
    AIClientError,
    CompletionResult,
    OpenAIClient,
)
from app.core.config import Settings


def _configured() -> Settings:
    return Settings(openai_api_key="sk-test", openai_model="gpt-test")


def test_not_configured_raises_immediately() -> None:
    client = OpenAIClient(Settings(openai_api_key=""))
    try:
        client.complete(
            [{"role": "user", "content": "hi"}],
            feature="analysis",
            timeout_seconds=1,
            max_tokens=10,
        )
    except AIClientError as exc:
        assert exc.reason == "NOT_CONFIGURED"
        assert exc.retryable is False
    else:
        raise AssertionError("expected AIClientError")


def test_timeout_retries_once() -> None:
    calls = {"n": 0}

    def sender(*_args, **_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            raise AIClientError(REASON_TIMEOUT, "timeout", retryable=True)
        return CompletionResult(text="{}", model="gpt-test")

    client = OpenAIClient(_configured(), sleep=lambda _s: None, sender=sender)
    result = client.complete(
        [{"role": "user", "content": "hi"}],
        feature="analysis",
        timeout_seconds=1,
        max_tokens=10,
    )
    assert result.text == "{}"
    assert calls["n"] == 2


def test_provider_5xx_retries_once_then_raises() -> None:
    calls = {"n": 0}

    def sender(*_args, **_kwargs):
        calls["n"] += 1
        raise AIClientError(REASON_PROVIDER_ERROR, "500", retryable=True)

    client = OpenAIClient(_configured(), sleep=lambda _s: None, sender=sender)
    try:
        client.complete(
            [{"role": "user", "content": "hi"}],
            feature="analysis",
            timeout_seconds=1,
            max_tokens=10,
        )
    except AIClientError as exc:
        assert exc.reason == REASON_PROVIDER_ERROR
    else:
        raise AssertionError("expected AIClientError")
    assert calls["n"] == 2


def test_4xx_does_not_retry() -> None:
    calls = {"n": 0}

    def sender(*_args, **_kwargs):
        calls["n"] += 1
        raise AIClientError(REASON_PROVIDER_ERROR, "400", retryable=False)

    client = OpenAIClient(_configured(), sleep=lambda _s: None, sender=sender)
    try:
        client.complete(
            [{"role": "user", "content": "hi"}],
            feature="analysis",
            timeout_seconds=1,
            max_tokens=10,
        )
    except AIClientError as exc:
        assert exc.retryable is False
    else:
        raise AssertionError("expected AIClientError")
    assert calls["n"] == 1
