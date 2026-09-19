from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_REPO_ROOT = _BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(_BACKEND_DIR / ".env", _REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    database_url: str = "sqlite:///./advisor.db"
    jwt_secret_key: str = "change-me"
    jwt_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    openai_api_key: str = ""
    openai_model: str = ""
    ai_timeout_seconds: int = 20
    ai_plan_timeout_seconds: int = 40
    ai_daily_analysis_limit: int = 10
    ai_daily_chat_limit: int = 30
    ai_daily_plan_limit: int = 5
    ai_max_tokens_analysis: int = 800
    ai_max_tokens_plan: int = 1200
    ai_max_tokens_chat: int = 600
    ai_cache_ttl_hours: int = 24
    ai_retry_backoff_seconds: float = 1.0

    @property
    def openai_configured(self) -> bool:
        return bool(self.openai_api_key.strip())

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


class UnsafeJwtSecretError(RuntimeError):
    """Raised when a non-dev environment still uses the placeholder JWT secret."""


def validate_settings(settings: Settings) -> None:
    if settings.app_env != "dev" and settings.jwt_secret_key == "change-me":
        raise UnsafeJwtSecretError(
            "JWT_SECRET_KEY must be changed when APP_ENV is not 'dev'."
        )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    validate_settings(settings)
    return settings
