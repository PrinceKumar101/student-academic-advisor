from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

from app.models.enums import AssessmentType


def _world(db_session: Session, demo_password_hash: str):
    _ua, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
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
    _uo, _other = add_teacher(
        db_session, password_hash=demo_password_hash, email="other@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    other_subject = add_subject(db_session, code="CS302", name="OS")
    enrollment = enroll(db_session, student_a, subject)
    assign_teacher(db_session, teacher, subject)
    assign_teacher(db_session, _other, other_subject)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 6, 1),
        classes_held=10,
        classes_attended=8,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 6, 2),
        name="I1",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=100,
        obtained_marks=72,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 6, 9),
        name="I2",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=100,
        obtained_marks=69,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 6, 16),
        name="I3",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=100,
        obtained_marks=63,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 6, 23),
        name="I4",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=100,
        obtained_marks=55,
    )
    return student_a, student_b


def test_trends_and_warnings_authorization(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    outsider = bearer(auth_client, "other@demo.edu")

    trends = auth_client.get("/api/v1/trends/me?as_of=2026-09-19", headers=a)
    assert trends.status_code == 200
    body = trends.json()
    assert body["student_id"] == student_a.id
    assert body["overall"]["label"] == "DECLINING"
    assert body["overall"]["slope"] == -5.7

    warnings = auth_client.get(
        "/api/v1/trends/me/warnings?as_of=2026-09-19", headers=a
    )
    assert warnings.status_code == 200
    assert "warnings" in warnings.json()

    forbidden = auth_client.get(
        f"/api/v1/trends/{student_a.id}?as_of=2026-09-19", headers=b
    )
    assert forbidden.status_code == 403

    visible = auth_client.get(
        f"/api/v1/trends/{student_a.id}?as_of=2026-09-19", headers=teacher
    )
    assert visible.status_code == 200

    hidden = auth_client.get(
        f"/api/v1/trends/{student_a.id}?as_of=2026-09-19", headers=outsider
    )
    assert hidden.status_code == 403
    assert student_b.id


def test_empty_student_trends(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="empty@demo.edu",
        student_code="E001",
    )
    headers = bearer(auth_client, "empty@demo.edu")
    response = auth_client.get("/api/v1/trends/me?as_of=2026-09-19", headers=headers)
    assert response.status_code == 200
    assert response.json()["overall"]["label"] == "INSUFFICIENT_DATA"
    warnings = auth_client.get(
        "/api/v1/trends/me/warnings?as_of=2026-09-19", headers=headers
    )
    assert warnings.json()["warnings"] == []
