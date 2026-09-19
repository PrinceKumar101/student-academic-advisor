from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_attendance,
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)


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
    return student_a, student_b


def test_risk_me_and_authorization(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    outsider = bearer(auth_client, "other@demo.edu")

    own = auth_client.get("/api/v1/risk/me?as_of=2026-09-19", headers=a)
    assert own.status_code == 200
    body = own.json()
    assert body["student_id"] == student_a.id
    assert body["as_of"] == "2026-09-19"
    assert body["level"] in ("LOW", "MEDIUM", "HIGH", "INSUFFICIENT_DATA")
    assert "components" in body
    assert "top_factors" in body

    forbidden = auth_client.get(
        f"/api/v1/risk/{student_a.id}?as_of=2026-09-19", headers=b
    )
    assert forbidden.status_code == 403

    visible = auth_client.get(
        f"/api/v1/risk/{student_a.id}?as_of=2026-09-19", headers=teacher
    )
    assert visible.status_code == 200

    hidden = auth_client.get(
        f"/api/v1/risk/{student_a.id}?as_of=2026-09-19", headers=outsider
    )
    assert hidden.status_code == 403

    hidden_b = auth_client.get(
        f"/api/v1/risk/{student_b.id}?as_of=2026-09-19", headers=teacher
    )
    assert hidden_b.status_code == 403

    history = auth_client.get("/api/v1/risk/me/history", headers=a)
    assert history.status_code == 200
    assert history.json()["student_id"] == student_a.id
    assert len(history.json()["items"]) >= 1
