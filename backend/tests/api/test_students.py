from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_semester_result,
    add_student,
    add_study_habit,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)


def _setup(
    db_session: Session, demo_password_hash: str
) -> tuple[int, int]:
    _user_a, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        full_name="Ada",
    )
    _user_b, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
    )
    _user_t, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    _user_other, other_teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="other@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    enroll(db_session, student_a, subject)
    assign_teacher(db_session, teacher, subject)
    add_study_habit(db_session, student_a, study_hours_per_day=2.5, self_confidence=4)
    add_semester_result(db_session, student_a, semester=4, percentage=78.0, sgpa=8.2)
    return student_a.id, student_b.id


def test_student_profile_access_matrix(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a_id, student_b_id = _setup(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")

    own = auth_client.get("/api/v1/students/me", headers=a)
    assert own.status_code == 200
    assert own.json()["student_code"] == "A001"
    assert own.json()["full_name"] == "Ada"

    other_student = auth_client.get(f"/api/v1/students/{student_a_id}", headers=b)
    assert other_student.status_code == 403

    visible = auth_client.get(f"/api/v1/students/{student_a_id}", headers=teacher)
    assert visible.status_code == 200

    hidden = auth_client.get(f"/api/v1/students/{student_a_id}", headers=other)
    assert hidden.status_code == 403

    missing = auth_client.get(f"/api/v1/students/{student_b_id}", headers=teacher)
    assert missing.status_code == 403


def test_study_habits_student_write_teacher_read(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a_id, _student_b_id = _setup(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")

    read = auth_client.get("/api/v1/students/me/study-habits", headers=a)
    assert read.status_code == 200
    assert read.json()["study_hours_per_day"] == 2.5

    teacher_read = auth_client.get(
        f"/api/v1/students/{student_a_id}/study-habits", headers=teacher
    )
    assert teacher_read.status_code == 200

    teacher_write = auth_client.put(
        f"/api/v1/students/{student_a_id}/study-habits",
        headers=teacher,
        json={
            "study_hours_per_day": 3,
            "self_confidence": 5,
            "available_hours_per_day": 4,
        },
    )
    assert teacher_write.status_code == 403

    updated = auth_client.put(
        "/api/v1/students/me/study-habits",
        headers=a,
        json={
            "study_hours_per_day": 3,
            "self_confidence": 5,
            "available_hours_per_day": 4,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["self_confidence"] == 5

    invalid = auth_client.put(
        "/api/v1/students/me/study-habits",
        headers=a,
        json={
            "study_hours_per_day": 30,
            "self_confidence": 5,
            "available_hours_per_day": 4,
        },
    )
    assert invalid.status_code == 422


def test_semester_results_teacher_write(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a_id, _student_b_id = _setup(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")

    listed = auth_client.get("/api/v1/students/me/semester-results", headers=a)
    assert listed.status_code == 200
    assert listed.json()[0]["percentage"] == 78.0

    student_put = auth_client.put(
        f"/api/v1/students/{student_a_id}/semester-results/3",
        headers=a,
        json={"percentage": 70, "sgpa": 7.5},
    )
    assert student_put.status_code == 403

    created = auth_client.put(
        f"/api/v1/students/{student_a_id}/semester-results/3",
        headers=teacher,
        json={"percentage": 70, "sgpa": 7.5},
    )
    assert created.status_code == 200
    assert created.json()["semester"] == 3

    updated = auth_client.put(
        f"/api/v1/students/{student_a_id}/semester-results/3",
        headers=teacher,
        json={"percentage": 72, "sgpa": 7.6},
    )
    assert updated.json()["percentage"] == 72.0
