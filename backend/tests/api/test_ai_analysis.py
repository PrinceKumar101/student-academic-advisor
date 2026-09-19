import json
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.ai.helpers import valid_advice_json
from tests.helpers import (
    add_attendance,
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

from app.ai.client import AIClientError, FakeAIClient, get_ai_client
from app.core.config import get_settings


def _world(db_session: Session, demo_password_hash: str):
    _user_a, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        full_name="Alice Example",
        section="A",
    )
    _ub, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        section="A",
    )
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    _uo, other = add_teacher(
        db_session, password_hash=demo_password_hash, email="other@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    other_subject = add_subject(db_session, code="CS302", name="OS")
    enrollment = enroll(db_session, student_a, subject)
    assign_teacher(db_session, teacher, subject)
    assign_teacher(db_session, other, other_subject)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=6,
    )
    return student_a


def _override(auth_app, client: FakeAIClient) -> None:
    auth_app.dependency_overrides[get_ai_client] = lambda: client


def _analyze(client: TestClient, headers: dict, *, refresh: bool = False):
    body: dict = {"student_id": "me"}
    if refresh:
        body["refresh"] = True
    return client.post("/api/v1/ai/analysis", json=body, headers=headers)


def test_happy_path_and_authorization(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    student_a = _world(db_session, demo_password_hash)
    fake = FakeAIClient(text=valid_advice_json())
    _override(auth_app, fake)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    outsider = bearer(auth_client, "other@demo.edu")

    own = auth_client.post("/api/v1/ai/analysis", json={"student_id": "me"}, headers=a)
    assert own.status_code == 200
    body = own.json()
    assert body["source"] == "AI"
    assert body["cached"] is False
    assert body["fallback_reason"] is None
    assert "facts" in body
    assert "advice" in body
    assert "Alice" not in str(body["facts"])
    assert "a@demo.edu" not in str(body["facts"])
    assert fake.calls == 1

    forbidden = auth_client.post(
        "/api/v1/ai/analysis",
        json={"student_id": str(student_a.id)},
        headers=b,
    )
    assert forbidden.status_code == 403

    visible = auth_client.post(
        "/api/v1/ai/analysis",
        json={"student_id": str(student_a.id)},
        headers=teacher,
    )
    assert visible.status_code == 200
    assert visible.json()["cached"] is True
    assert fake.calls == 1

    hidden = auth_client.post(
        "/api/v1/ai/analysis",
        json={"student_id": str(student_a.id)},
        headers=outsider,
    )
    assert hidden.status_code == 403


def test_cache_hit_skips_client_and_limit(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    _world(db_session, demo_password_hash)
    fake = FakeAIClient(text=valid_advice_json())
    _override(auth_app, fake)
    headers = bearer(auth_client, "a@demo.edu")
    first = _analyze(auth_client, headers)
    second = _analyze(auth_client, headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["cached"] is True
    assert fake.calls == 1
    usage = auth_client.get("/api/v1/ai/usage", headers=headers)
    assert usage.status_code == 200
    assert usage.json()["analysis"]["used"] == 1


def test_timeout_and_invalid_outputs_fall_back(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    _world(db_session, demo_password_hash)
    headers = bearer(auth_client, "a@demo.edu")

    _override(
        auth_app,
        FakeAIClient(error=AIClientError("TIMEOUT", "late", retryable=True)),
    )
    timeout = _analyze(auth_client, headers, refresh=True)
    assert timeout.status_code == 200
    assert timeout.json()["source"] == "FALLBACK"
    assert timeout.json()["fallback_reason"] == "TIMEOUT"

    _override(auth_app, FakeAIClient(text="not-json"))
    invalid = _analyze(auth_client, headers, refresh=True)
    assert invalid.json()["fallback_reason"] == "INVALID_OUTPUT"

    payload = {
        "summary": "Attendance is 99%.",
        "main_concerns": [
            {"factor": "attendance", "explanation": "Invented figure."}
        ],
        "recommendations": [
            {"action": "A", "reason": "r", "priority": "HIGH"},
            {"action": "B", "reason": "r", "priority": "MEDIUM"},
            {"action": "C", "reason": "r", "priority": "LOW"},
        ],
        "priority": "HIGH",
    }
    _override(auth_app, FakeAIClient(text=json.dumps(payload)))
    ungrounded = _analyze(auth_client, headers, refresh=True)
    assert ungrounded.json()["fallback_reason"] == "UNGROUNDED_OUTPUT"


def test_not_configured_and_risk_still_works(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    _world(db_session, demo_password_hash)
    _override(
        auth_app,
        FakeAIClient(
            error=AIClientError("NOT_CONFIGURED", "no key", retryable=False)
        ),
    )
    headers = bearer(auth_client, "a@demo.edu")
    analysis = auth_client.post(
        "/api/v1/ai/analysis", json={"student_id": "me"}, headers=headers
    )
    assert analysis.status_code == 200
    assert analysis.json()["source"] == "FALLBACK"
    assert analysis.json()["fallback_reason"] == "NOT_CONFIGURED"
    risk = auth_client.get("/api/v1/risk/me?as_of=2026-09-19", headers=headers)
    assert risk.status_code == 200
    assert "score" in risk.json()


def test_daily_limit_returns_429(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
    monkeypatch,
) -> None:
    _world(db_session, demo_password_hash)
    settings = get_settings()
    monkeypatch.setattr(settings, "ai_daily_analysis_limit", 1)
    _override(auth_app, FakeAIClient(text=valid_advice_json()))
    headers = bearer(auth_client, "a@demo.edu")
    first = _analyze(auth_client, headers)
    assert first.status_code == 200
    second = auth_client.post(
        "/api/v1/ai/analysis",
        json={"student_id": "me", "refresh": True},
        headers=headers,
    )
    assert second.status_code == 429
    assert second.json()["error"]["code"] == "RATE_LIMITED"
