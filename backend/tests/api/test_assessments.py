from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)

from app.models.enums import AssessmentStatus, AssessmentType


def _world(db_session: Session, demo_password_hash: str):
    _ua, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    _ub, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
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
    add_assessment(
        db_session,
        enrollment,
        assessment_date=date(2026, 9, 1),
        name="Internal 1",
        assessment_type=AssessmentType.INTERNAL,
        max_marks=20,
        obtained_marks=16,
    )
    return student_a, student_b, subject, other_subject


def test_assessment_list_and_filters(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, _b, subject, _other = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    listed = auth_client.get("/api/v1/assessments?student_id=me", headers=a)
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["type"] == "INTERNAL"

    filtered = auth_client.get(
        f"/api/v1/assessments?student_id=me&subject_id={subject.id}&type=QUIZ",
        headers=a,
    )
    assert filtered.json() == []
    _ = student_a


def test_assessment_permissions_and_rules(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b, subject, _other = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")

    assert (
        auth_client.get(
            f"/api/v1/assessments?student_id={student_a.id}", headers=b
        ).status_code
        == 403
    )
    assert (
        auth_client.get(
            f"/api/v1/assessments?student_id={student_a.id}", headers=other
        ).status_code
        == 403
    )
    assert (
        auth_client.get(
            f"/api/v1/assessments?student_id={student_a.id}", headers=teacher
        ).status_code
        == 200
    )

    student_post = auth_client.post(
        "/api/v1/assessments",
        headers=a,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "type": "QUIZ",
            "name": "Q2",
            "max_marks": 10,
            "obtained_marks": 8,
            "status": "GRADED",
            "assessment_date": "2026-09-10",
        },
    )
    assert student_post.status_code == 403

    graded_missing = auth_client.post(
        "/api/v1/assessments",
        headers=teacher,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "type": "QUIZ",
            "name": "Q2",
            "max_marks": 10,
            "obtained_marks": None,
            "status": "GRADED",
            "assessment_date": "2026-09-10",
        },
    )
    assert graded_missing.status_code == 422

    over_max = auth_client.post(
        "/api/v1/assessments",
        headers=teacher,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "type": "QUIZ",
            "name": "Q2",
            "max_marks": 10,
            "obtained_marks": 12,
            "status": "GRADED",
            "assessment_date": "2026-09-10",
        },
    )
    assert over_max.status_code == 422

    created = auth_client.post(
        "/api/v1/assessments",
        headers=teacher,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "type": "QUIZ",
            "name": "Q2",
            "max_marks": 10,
            "obtained_marks": 8,
            "status": "GRADED",
            "assessment_date": "2026-09-10",
        },
    )
    assert created.status_code == 201
    assessment_id = created.json()["id"]

    other_put = auth_client.put(
        f"/api/v1/assessments/{assessment_id}",
        headers=other,
        json={"obtained_marks": 9},
    )
    assert other_put.status_code == 403

    updated = auth_client.put(
        f"/api/v1/assessments/{assessment_id}",
        headers=teacher,
        json={"obtained_marks": 9, "status": AssessmentStatus.GRADED.value},
    )
    assert updated.status_code == 200
    assert updated.json()["obtained_marks"] == 9

    deleted = auth_client.delete(
        f"/api/v1/assessments/{assessment_id}", headers=teacher
    )
    assert deleted.status_code == 204
    _ = student_b
