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


def test_subject_analysis_and_small_group_comparison(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _ua, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        section="A",
    )
    _ut, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    enrollment = enroll(db_session, student, subject)
    assign_teacher(db_session, teacher, subject)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 12),
        classes_held=10,
        classes_attended=6,
    )
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 9, 12),
        name="I1",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=100,
        obtained_marks=49.9,
    )

    headers = bearer(auth_client, "a@demo.edu")
    subjects = auth_client.get(
        "/api/v1/analytics/students/me/subjects?as_of=2026-09-19", headers=headers
    )
    assert subjects.status_code == 200
    item = subjects.json()["subjects"][0]
    assert item["band"] == "HIGH_CONCERN"
    assert item["attendance_alert"] is True

    comparison = auth_client.get(
        "/api/v1/analytics/students/me/comparison?as_of=2026-09-19",
        headers=headers,
    )
    assert comparison.status_code == 200
    body = comparison.json()
    assert body["available"] is False
    assert body["group_size"] == 1
    assert body["student"] is None
    assert body["class_average"] is None
