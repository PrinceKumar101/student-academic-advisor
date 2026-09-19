from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_student,
    add_subject,
    add_teacher,
    assign_teacher,
    bearer,
    enroll,
)


def test_list_subjects_mine_and_all(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _user_a, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    _user_t, teacher = add_teacher(
        db_session, password_hash=demo_password_hash, email="t@demo.edu"
    )
    cs301 = add_subject(db_session, code="CS301", name="DSA")
    add_subject(db_session, code="CS302", name="OS")
    enroll(db_session, student_a, cs301)
    assign_teacher(db_session, teacher, cs301)

    student_headers = bearer(auth_client, "a@demo.edu")
    mine = auth_client.get("/api/v1/subjects?mine=true", headers=student_headers)
    assert mine.status_code == 200
    assert [item["code"] for item in mine.json()["items"]] == ["CS301"]
    assert mine.json()["total"] == 1

    all_subjects = auth_client.get("/api/v1/subjects", headers=student_headers)
    assert all_subjects.status_code == 200
    assert all_subjects.json()["total"] == 2

    teacher_headers = bearer(auth_client, "t@demo.edu")
    taught = auth_client.get("/api/v1/subjects?mine=true", headers=teacher_headers)
    assert [item["code"] for item in taught.json()["items"]] == ["CS301"]


def test_create_subject_assigns_teacher(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    add_teacher(db_session, password_hash=demo_password_hash, email="t@demo.edu")
    add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
    )
    student_headers = bearer(auth_client, "a@demo.edu")
    denied = auth_client.post(
        "/api/v1/subjects",
        headers=student_headers,
        json={"code": "CS310", "name": "ML", "semester": 5},
    )
    assert denied.status_code == 403

    teacher_headers = bearer(auth_client, "t@demo.edu")
    created = auth_client.post(
        "/api/v1/subjects",
        headers=teacher_headers,
        json={"code": "CS310", "name": "ML", "semester": 5},
    )
    assert created.status_code == 201
    subject_id = created.json()["id"]
    mine = auth_client.get("/api/v1/subjects?mine=true", headers=teacher_headers)
    assert subject_id in {item["id"] for item in mine.json()["items"]}

    duplicate = auth_client.post(
        "/api/v1/subjects",
        headers=teacher_headers,
        json={"code": "CS310", "name": "ML2", "semester": 5},
    )
    assert duplicate.status_code == 409


def test_patch_and_enroll_permissions(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _user_a, student_a = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
        section="A",
    )
    _user_b, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        section="B",
    )
    _user_t1, teacher1 = add_teacher(
        db_session, password_hash=demo_password_hash, email="t1@demo.edu"
    )
    _user_t2, teacher2 = add_teacher(
        db_session, password_hash=demo_password_hash, email="t2@demo.edu"
    )
    subject = add_subject(db_session, code="CS301", name="DSA")
    assign_teacher(db_session, teacher1, subject, section="A")
    assign_teacher(db_session, teacher2, subject, section="B")

    t1 = bearer(auth_client, "t1@demo.edu")
    t2 = bearer(auth_client, "t2@demo.edu")

    patched = auth_client.patch(
        f"/api/v1/subjects/{subject.id}",
        headers=t1,
        json={"name": "Data Structures"},
    )
    assert patched.status_code == 200
    assert patched.json()["name"] == "Data Structures"

    enroll_a = auth_client.post(
        f"/api/v1/subjects/{subject.id}/enrollments",
        headers=t1,
        json={"student_id": student_a.id},
    )
    assert enroll_a.status_code == 201

    enroll_b_denied = auth_client.post(
        f"/api/v1/subjects/{subject.id}/enrollments",
        headers=t1,
        json={"student_id": student_b.id},
    )
    assert enroll_b_denied.status_code == 403

    enroll_b = auth_client.post(
        f"/api/v1/subjects/{subject.id}/enrollments",
        headers=t2,
        json={"student_id": student_b.id},
    )
    assert enroll_b.status_code == 201

    again = auth_client.post(
        f"/api/v1/subjects/{subject.id}/enrollments",
        headers=t1,
        json={"student_id": student_a.id},
    )
    assert again.status_code == 409

    unenroll_denied = auth_client.delete(
        f"/api/v1/subjects/{subject.id}/enrollments/{student_b.id}",
        headers=t1,
    )
    assert unenroll_denied.status_code == 403

    unenroll = auth_client.delete(
        f"/api/v1/subjects/{subject.id}/enrollments/{student_a.id}",
        headers=t1,
    )
    assert unenroll.status_code == 204


def test_subjects_require_auth(auth_client: TestClient) -> None:
    response = auth_client.get("/api/v1/subjects")
    assert response.status_code == 401
