from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_attendance,
    add_semester_result,
    add_student,
    add_study_habit,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

import app.models  # noqa: F401 — register tables on Base.metadata
from app.db.base import Base
from app.models.enums import AssessmentStatus, AssessmentType


def _snapshot(db: Session) -> dict[str, list[dict]]:
    data: dict[str, list[dict]] = {}
    for table in Base.metadata.sorted_tables:
        rows = db.execute(select(table)).mappings().all()
        data[table.name] = [dict(row) for row in rows]
    return data


def _r3_world(db_session: Session, demo_password_hash: str):
    _ua, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="r3@demo.edu",
        student_code="R3001",
        section="A",
    )
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="other@demo.edu",
        student_code="O001",
        section="A",
    )
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    _uo, outsider = add_teacher(
        db_session, password_hash=demo_password_hash, email="out@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    other_subject = add_subject(db_session, code="CS302", name="OS")
    enrollment = enroll(db_session, student, subject)
    assign_teacher(db_session, teacher, subject)
    assign_teacher(db_session, outsider, other_subject)
    on = date(2026, 9, 12)
    add_attendance(
        db_session,
        enrollment,
        record_date=on,
        classes_held=100,
        classes_attended=64,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="Internal",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=100,
        obtained_marks=45,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="Quiz",
        assessment_type=AssessmentType.QUIZ,
        max_marks=100,
        obtained_marks=40,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="A1",
        assessment_type=AssessmentType.ASSIGNMENT,
        max_marks=100,
        obtained_marks=50,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="A2",
        assessment_type=AssessmentType.ASSIGNMENT,
        max_marks=100,
        obtained_marks=50,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="A3",
        assessment_type=AssessmentType.ASSIGNMENT,
        max_marks=100,
        obtained_marks=50,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="Missing 1",
        assessment_type=AssessmentType.ASSIGNMENT,
        max_marks=100,
        obtained_marks=None,
        status=AssessmentStatus.MISSING,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=on,
        name="Missing 2",
        assessment_type=AssessmentType.ASSIGNMENT,
        max_marks=100,
        obtained_marks=None,
        status=AssessmentStatus.MISSING,
    )
    add_semester_result(db_session, student, semester=4, percentage=55)
    add_study_habit(
        db_session, student, study_hours_per_day=1, self_confidence=2
    )
    return student


def test_what_if_w1_and_does_not_write(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student = _r3_world(db_session, demo_password_hash)
    headers = bearer(auth_client, "r3@demo.edu")
    before = _snapshot(db_session)

    response = auth_client.post(
        f"/api/v1/risk/{student.id}/what-if?as_of=2026-09-19",
        headers=headers,
        json={"overrides": {"attendance_percent": 80}},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["persisted"] is False
    assert body["current"]["score"] == 67.1
    assert body["current"]["level"] == "HIGH"
    assert body["simulated"]["score"] == 57.1
    assert body["simulated"]["level"] == "MEDIUM"
    assert body["difference"] == -10.0
    factor = body["changed_factors"][0]
    assert factor["key"] == "attendance"
    assert factor["risk_from"] == 65.0
    assert factor["risk_to"] == 25.0
    assert factor["contribution_delta"] == -10.0
    assert factor["hypothetical"] is False

    after = _snapshot(db_session)
    assert after == before

    empty = auth_client.post(
        "/api/v1/risk/me/what-if?as_of=2026-09-19",
        headers=headers,
        json={"overrides": {}},
    )
    assert empty.status_code == 200
    assert empty.json()["difference"] == 0.0
    assert _snapshot(db_session) == before

    forbidden = auth_client.post(
        f"/api/v1/risk/{student.id}/what-if",
        headers=bearer(auth_client, "other@demo.edu"),
        json={"overrides": {"attendance_percent": 80}},
    )
    assert forbidden.status_code == 403
    assert _snapshot(db_session) == before

    teacher = auth_client.post(
        f"/api/v1/risk/{student.id}/what-if?as_of=2026-09-19",
        headers=bearer(auth_client, "t@demo.edu"),
        json={"overrides": {"attendance_percent": 80}},
    )
    assert teacher.status_code == 200
    assert teacher.json()["difference"] == -10.0

    hidden = auth_client.post(
        f"/api/v1/risk/{student.id}/what-if",
        headers=bearer(auth_client, "out@demo.edu"),
        json={"overrides": {"attendance_percent": 80}},
    )
    assert hidden.status_code == 403
    assert _snapshot(db_session) == before


def test_what_if_validation(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _r3_world(db_session, demo_password_hash)
    headers = bearer(auth_client, "r3@demo.edu")
    before = _snapshot(db_session)

    unknown = auth_client.post(
        "/api/v1/risk/me/what-if",
        headers=headers,
        json={"overrides": {"gpa": 9}},
    )
    assert unknown.status_code == 422
    assert unknown.json()["error"]["code"] == "VALIDATION_ERROR"

    oob = auth_client.post(
        "/api/v1/risk/me/what-if",
        headers=headers,
        json={"overrides": {"attendance_percent": 120}},
    )
    assert oob.status_code == 422
    assert _snapshot(db_session) == before
