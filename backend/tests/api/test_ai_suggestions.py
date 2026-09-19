import json
from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.ai.helpers import sample_context
from tests.helpers import (
    add_attendance,
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

from app.ai.client import FakeAIClient, get_ai_client
from app.ai.fallback import fallback_suggestions
from app.core.config import get_settings


def _valid_suggestions_json() -> str:
    return json.dumps(
        {
            "suggestions": [
                {
                    "title": "Attendance recovery meeting",
                    "description": "Discuss the attendance pattern with the student.",
                    "priority": "HIGH",
                    "reason": "Attendance is a leading computed risk factor.",
                }
            ]
        }
    )


def _world(db_session: Session, demo_password_hash: str):
    _ua, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        section="A",
    )
    _ub, _student_b = add_student(
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


def test_teacher_suggestions_and_fallback(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    student_a = _world(db_session, demo_password_hash)
    get_settings.cache_clear()
    auth_app.dependency_overrides[get_ai_client] = lambda: FakeAIClient(
        text=_valid_suggestions_json()
    )
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")
    student = bearer(auth_client, "a@demo.edu")

    student_denied = auth_client.post(
        "/api/v1/ai/intervention-suggestions",
        json={"student_id": "me"},
        headers=student,
    )
    assert student_denied.status_code == 403

    hidden = auth_client.post(
        "/api/v1/ai/intervention-suggestions",
        json={"student_id": str(student_a.id)},
        headers=other,
    )
    assert hidden.status_code == 403

    ok = auth_client.post(
        "/api/v1/ai/intervention-suggestions",
        json={"student_id": str(student_a.id)},
        headers=teacher,
    )
    assert ok.status_code == 200
    assert ok.json()["source"] == "AI"
    assert ok.json()["suggestions"]

    auth_app.dependency_overrides[get_ai_client] = lambda: FakeAIClient(
        text="not-json"
    )
    fallback = auth_client.post(
        "/api/v1/ai/intervention-suggestions",
        json={"student_id": str(student_a.id)},
        headers=teacher,
    )
    assert fallback.status_code == 200
    assert fallback.json()["source"] == "FALLBACK"
    assert fallback.json()["fallback_reason"] == "INVALID_OUTPUT"


def test_fallback_suggestions_are_valid() -> None:
    advice = fallback_suggestions(sample_context())
    assert 1 <= len(advice.suggestions) <= 5
