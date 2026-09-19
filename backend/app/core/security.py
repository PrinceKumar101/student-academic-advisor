from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings
from app.core.errors import Unauthenticated

_password_hash = PasswordHash.recommended()
JWT_ALGORITHM = "HS256"


def hash_password(plain: str) -> str:
    return _password_hash.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _password_hash.verify(plain, hashed)


def create_access_token(
    *,
    user_id: int,
    role: str,
    now: datetime | None = None,
    expires_minutes: int | None = None,
) -> str:
    settings = get_settings()
    issued_at = now or datetime.now(UTC)
    lifetime = (
        settings.jwt_expire_minutes if expires_minutes is None else expires_minutes
    )
    payload = {
        "sub": str(user_id),
        "role": role,
        "iat": issued_at,
        "exp": issued_at + timedelta(minutes=lifetime),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[JWT_ALGORITHM],
        )
    except jwt.InvalidTokenError as exc:
        raise Unauthenticated("Invalid or expired token") from exc
