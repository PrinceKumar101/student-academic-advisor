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
    enroll(db_session, student_a, other_subject)
    assign_teacher(db_session, teacher, subject)
    assign_teacher(db_session, other, other_subject)
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 5),
        classes_held=4,
        classes_attended=3,
    )
    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 12),
        classes_held=0,
        classes_attended=0,
    )
    return student_a, student_b, subject, other_subject, enrollment


def test_attendance_percent_and_zero_classes(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, _b, subject, other_subject, _enr = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    listed = auth_client.get("/api/v1/attendance?student_id=me", headers=a)
    assert listed.status_code == 200
    body = listed.json()
    cs301 = next(item for item in body["summaries"] if item["subject_id"] == subject.id)
    assert cs301["classes_held"] == 4
    assert cs301["classes_attended"] == 3
    assert cs301["attendance_percent"] == 75.0
    cs302 = next(
        item for item in body["summaries"] if item["subject_id"] == other_subject.id
    )
    assert cs302["attendance_percent"] is None

    filtered = auth_client.get(
        f"/api/v1/attendance?student_id=me&subject_id={subject.id}", headers=a
    )
    assert len(filtered.json()["summaries"]) == 1


def test_attendance_access_and_writes(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b, subject, other_subject, enrollment = _world(
        db_session, demo_password_hash
    )
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")

    assert (
        auth_client.get(
            f"/api/v1/attendance?student_id={student_a.id}", headers=b
        ).status_code
        == 403
    )
    assert (
        auth_client.get(
            f"/api/v1/attendance?student_id={student_a.id}", headers=other
        ).status_code
        == 200
    )
    assert (
        auth_client.get(
            f"/api/v1/attendance?student_id={student_a.id}", headers=teacher
        ).status_code
        == 200
    )

    student_write = auth_client.post(
        "/api/v1/attendance",
        headers=a,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "record_date": "2026-09-19",
            "classes_held": 2,
            "classes_attended": 2,
        },
    )
    assert student_write.status_code == 403

    other_write = auth_client.post(
        "/api/v1/attendance",
        headers=other,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "record_date": "2026-09-19",
            "classes_held": 2,
            "classes_attended": 2,
        },
    )
    assert other_write.status_code == 403

    created = auth_client.post(
        "/api/v1/attendance",
        headers=teacher,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "record_date": "2026-09-19",
            "classes_held": 2,
            "classes_attended": 2,
        },
    )
    assert created.status_code == 201
    record_id = created.json()["id"]

    invalid = auth_client.post(
        "/api/v1/attendance",
        headers=teacher,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "record_date": "2026-09-20",
            "classes_held": 2,
            "classes_attended": 3,
        },
    )
    assert invalid.status_code == 422

    duplicate = auth_client.post(
        "/api/v1/attendance",
        headers=teacher,
        json={
            "student_id": student_a.id,
            "subject_id": subject.id,
            "record_date": "2026-09-19",
            "classes_held": 1,
            "classes_attended": 1,
        },
    )
    assert duplicate.status_code == 409

    updated = auth_client.put(
        f"/api/v1/attendance/{record_id}",
        headers=teacher,
        json={"classes_held": 3, "classes_attended": 2},
    )
    assert updated.status_code == 200
    assert updated.json()["classes_held"] == 3

    other_update = auth_client.put(
        f"/api/v1/attendance/{record_id}",
        headers=other,
        json={"classes_held": 4, "classes_attended": 4},
    )
    assert other_update.status_code == 403

    deleted = auth_client.delete(f"/api/v1/attendance/{record_id}", headers=teacher)
    assert deleted.status_code == 204
    assert enrollment.id is not None
    _ = other_subject
    _ = student_b
