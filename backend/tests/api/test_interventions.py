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
    _ub, student_b = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="b@demo.edu",
        student_code="B001",
        full_name="Bea",
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
    return student_a, student_b, subject, enrollment


def _create(client: TestClient, headers: dict, student_id: int, **extra):
    body = {
        "student_id": student_id,
        "title": "Weekly attendance check-in",
        "description": "Meet twice this week.",
        "priority": "HIGH",
        **extra,
    }
    return client.post(
        f"/api/v1/interventions?as_of={AS_OF}",
        json=body,
        headers=headers,
    )


def test_create_visibility_and_baseline(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b, _subject, enrollment = _world(
        db_session, demo_password_hash
    )
    teacher = bearer(auth_client, "t@demo.edu")
    other = bearer(auth_client, "other@demo.edu")
    student = bearer(auth_client, "a@demo.edu")

    forbidden = _create(auth_client, other, student_a.id)
    assert forbidden.status_code == 403

    student_create = _create(auth_client, student, student_a.id)
    assert student_create.status_code == 403

    hidden = _create(auth_client, teacher, student_b.id)
    assert hidden.status_code == 403

    created = _create(auth_client, teacher, student_a.id)
    assert created.status_code == 201
    payload = created.json()
    assert payload["student_id"] == student_a.id
    assert payload["status"] == "PENDING"
    assert payload["baseline_level"]
    baseline_score = payload["baseline_score"]
    intervention_id = payload["id"]

    add_attendance(
        db_session,
        enrollment,
        record_date=date(2026, 9, 19),
        classes_held=10,
        classes_attended=10,
    )
    detail = auth_client.get(
        f"/api/v1/interventions/{intervention_id}", headers=teacher
    )
    assert detail.status_code == 200
    assert detail.json()["baseline_score"] == baseline_score

    progress = auth_client.get(
        f"/api/v1/interventions/{intervention_id}/progress?as_of={AS_OF}",
        headers=teacher,
    )
    assert progress.status_code == 200
    body = progress.json()
    assert body["baseline"]["score"] == baseline_score
    assert body["note"].startswith("This shows the observed change")
    assert body["direction"] in {"IMPROVED", "WORSENED", "UNCHANGED"}


def test_student_list_and_forward_status(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    student_a, student_b, _subject, _enrollment = _world(
        db_session, demo_password_hash
    )
    teacher = bearer(auth_client, "t@demo.edu")
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    created = _create(auth_client, teacher, student_a.id)
    intervention_id = created.json()["id"]

    own = auth_client.get("/api/v1/interventions", headers=a)
    assert own.status_code == 200
    assert len(own.json()) == 1

    other_list = auth_client.get("/api/v1/interventions", headers=b)
    assert other_list.status_code == 200
    assert other_list.json() == []

    other_get = auth_client.get(
        f"/api/v1/interventions/{intervention_id}", headers=b
    )
    assert other_get.status_code == 403

    field_denied = auth_client.patch(
        f"/api/v1/interventions/{intervention_id}",
        json={"title": "Hacked"},
        headers=a,
    )
    assert field_denied.status_code == 403

    skip = auth_client.patch(
        f"/api/v1/interventions/{intervention_id}",
        json={"status": "COMPLETED"},
        headers=a,
    )
    assert skip.status_code == 422

    start = auth_client.patch(
        f"/api/v1/interventions/{intervention_id}",
        json={"status": "IN_PROGRESS"},
        headers=a,
    )
    assert start.status_code == 200
    assert start.json()["status"] == "IN_PROGRESS"

    done = auth_client.patch(
        f"/api/v1/interventions/{intervention_id}?as_of={AS_OF}",
        json={"status": "COMPLETED", "completion_note": "Attended extra class"},
        headers=a,
    )
    assert done.status_code == 200
    assert done.json()["status"] == "COMPLETED"
    assert done.json()["outcome_level"] is not None
    assert done.json()["completion_note"] == "Attended extra class"

    regress = auth_client.patch(
        f"/api/v1/interventions/{intervention_id}",
        json={"status": "PENDING"},
        headers=a,
    )
    assert regress.status_code == 422

    reopen = auth_client.patch(
        f"/api/v1/interventions/{intervention_id}",
        json={"status": "IN_PROGRESS"},
        headers=teacher,
    )
    assert reopen.status_code == 200
    assert reopen.json()["status"] == "IN_PROGRESS"
