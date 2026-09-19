from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import add_student, bearer

from app.core.config import Settings, UnsafeJwtSecretError, validate_settings

ROOT = Path(__file__).resolve().parents[3]
BACKEND = Path(__file__).resolve().parents[2]


def test_env_example_has_blank_ai_key() -> None:
    text = (ROOT / ".env.example").read_text(encoding="utf-8")
    assert "OPENAI_API_KEY=" in text
    for line in text.splitlines():
        if line.startswith("OPENAI_API_KEY="):
            assert line.strip() == "OPENAI_API_KEY="


def test_no_hardcoded_provider_secrets_in_app() -> None:
    forbidden = ("sk-", "OPENAI_API_KEY = \"sk")
    for path in (BACKEND / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{path} contains {token}"


def test_default_jwt_secret_rejected_outside_dev() -> None:
    try:
        validate_settings(Settings(app_env="prod", jwt_secret_key="change-me"))
    except UnsafeJwtSecretError:
        return
    raise AssertionError("expected UnsafeJwtSecretError")


def test_password_hash_never_in_me(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    headers = bearer(auth_client, "a@demo.edu")
    response = auth_client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    assert "password" not in response.text.lower()
    assert "password_hash" not in response.json()
