from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_attendance,
    add_student,
    add_study_habit,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

from app.models.enums import InterventionStatus

AS_OF = "2026-09-19"


def _world(db_session: Session, demo_password_hash: str):
    _ua, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        full_name="Ada",
        section="A",
    )
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        section="A",
    )
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    add_teacher(db_session, password_hash=demo_password_hash, email="other@demo.edu")
    subject = add_subject(db_session, code="CS301", name="DSA")
    enrollment = enroll(db_session, student_a, subject)
    assign_teacher(db_session, teacher, subject)
    add_study_habit(db_session, student_a)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=6,
    )
    return student_a


def test_overview_composite_and_access(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")

    created = auth_client.post(
        f"/api/v1/interventions?as_of={AS_OF}",
        headers=teacher,
        json={"student_id": student_a.id, "title": "Check attendance"},
    )
    assert created.status_code == 201

    own = auth_client.get(f"/api/v1/students/me/overview?as_of={AS_OF}", headers=a)
    assert own.status_code == 200
    body = own.json()
    assert body["student_id"] == student_a.id
    assert body["profile"]["student_code"] == "A001"
    assert body["risk"]["level"]
    assert "top_factors" in body
    assert "subjects" in body
    assert "trend_summary" in body
    assert "warnings" in body
    assert len(body["open_interventions"]) == 1
    assert body["open_interventions"][0]["status"] == InterventionStatus.PENDING

    teacher_view = auth_client.get(
        f"/api/v1/students/{student_a.id}/overview?as_of={AS_OF}", headers=teacher
    )
    assert teacher_view.status_code == 200
    assert teacher_view.json()["profile"]["full_name"] == "Ada"

    assert (
        auth_client.get(
            f"/api/v1/students/{student_a.id}/overview", headers=b
        ).status_code
        == 403
    )
    assert (
        auth_client.get(
            f"/api/v1/students/{student_a.id}/overview", headers=other
        ).status_code
        == 403
    )
    assert auth_client.get("/api/v1/students/me/overview").status_code == 401
