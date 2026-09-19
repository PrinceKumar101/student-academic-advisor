from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.errors import Unauthenticated
from app.core.security import JWT_ALGORITHM, create_access_token, decode_access_token


def test_create_and_decode_round_trip() -> None:
    token = create_access_token(user_id=42, role="STUDENT")
    payload = decode_access_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "STUDENT"
    assert "iat" in payload
    assert "exp" in payload


def test_expired_token_raises_unauthenticated() -> None:
    issued = datetime.now(UTC) - timedelta(hours=2)
    token = create_access_token(
        user_id=1,
        role="STUDENT",
        now=issued,
        expires_minutes=1,
    )
    with pytest.raises(Unauthenticated) as exc:
        decode_access_token(token)
    assert exc.value.status_code == 401
    assert exc.value.message == "Invalid or expired token"


def test_tampered_token_raises_unauthenticated() -> None:
    token = create_access_token(user_id=1, role="STUDENT")
    tampered = token[:-2] + ("A" if token[-2] != "A" else "B") + token[-1]
    with pytest.raises(Unauthenticated) as exc:
        decode_access_token(tampered)
    assert exc.value.message == "Invalid or expired token"


def test_wrong_secret_raises_unauthenticated() -> None:
    token = jwt.encode(
        {"sub": "1", "role": "STUDENT"},
        "other-secret",
        algorithm=JWT_ALGORITHM,
    )
    with pytest.raises(Unauthenticated):
        decode_access_token(token)
