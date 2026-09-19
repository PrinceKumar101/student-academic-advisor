import pytest

from app.core.config import Settings, UnsafeJwtSecretError, validate_settings


def test_jwt_guard_rejects_placeholder_outside_dev() -> None:
    settings = Settings(app_env="prod", jwt_secret_key="change-me")
    with pytest.raises(UnsafeJwtSecretError):
        validate_settings(settings)


def test_jwt_guard_allows_placeholder_in_dev() -> None:
    validate_settings(Settings(app_env="dev", jwt_secret_key="change-me"))


def test_cors_origin_list_splits_and_strips() -> None:
    settings = Settings(cors_origins="http://localhost:5173, https://example.test")
    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "https://example.test",
    ]
