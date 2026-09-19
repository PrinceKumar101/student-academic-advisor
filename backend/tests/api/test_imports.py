from datetime import date

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


def _world(db_session: Session, demo_password_hash: str):
    _ua, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="a@demo.edu",
        student_code="A001",
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
    enroll(db_session, student, subject)
    assign_teacher(db_session, teacher, subject)
    return student


def test_csv_import_dry_run_then_commit(
    auth_client: TestClient, db_session: Session, demo_password_hash: str
) -> None:
    _world(db_session, demo_password_hash)
    teacher = bearer(auth_client, "t@demo.edu")
    student = bearer(auth_client, "a@demo.edu")
    other = bearer(auth_client, "other@demo.edu")

    attendance_csv = (
        b"student_code,subject_code,record_date,classes_held,classes_attended\n"
        b"A001,CS301,2026-09-05,5,4\n"
        b"A001,CS301,2026-09-05,5,3\n"
    )
    dry = auth_client.post(
        "/api/v1/imports/attendance?dry_run=true",
        headers=teacher,
        files={"file": ("att.csv", attendance_csv, "text/csv")},
    )
    assert dry.status_code == 200
    assert dry.json()["committed"] is False
    assert dry.json()["valid"] is False
    assert dry.json()["errors"][0]["code"] == "CONFLICT"

    good = (
        b"student_code,subject_code,record_date,classes_held,classes_attended\n"
        b"A001,CS301,2026-09-05,5,4\n"
    )
    preview = auth_client.post(
        "/api/v1/imports/attendance?dry_run=true",
        headers=teacher,
        files={"file": ("att.csv", good, "text/csv")},
    )
    assert preview.json()["valid"] is True
    assert preview.json()["committed"] is False

    listed = auth_client.get("/api/v1/attendance?student_id=me", headers=student)
    assert listed.json()["records"] == []

    committed = auth_client.post(
        "/api/v1/imports/attendance?dry_run=false",
        headers=teacher,
        files={"file": ("att.csv", good, "text/csv")},
    )
    assert committed.status_code == 200
    assert committed.json()["committed"] is True
    assert committed.json()["created_count"] == 1

    listed = auth_client.get("/api/v1/attendance?student_id=me", headers=student)
    assert len(listed.json()["records"]) == 1
    assert listed.json()["summaries"][0]["attendance_percent"] == 80.0

    forbidden = auth_client.post(
        "/api/v1/imports/attendance?dry_run=true",
        headers=other,
        files={"file": ("att.csv", good, "text/csv")},
    )
    assert forbidden.status_code == 200
    assert forbidden.json()["valid"] is False
    assert forbidden.json()["errors"][0]["code"] == "FORBIDDEN"

    student_write = auth_client.post(
        "/api/v1/imports/attendance?dry_run=true",
        headers=student,
        files={"file": ("att.csv", good, "text/csv")},
    )
    assert student_write.status_code == 403

    assessments = (
        b"student_code,subject_code,type,name,max_marks,obtained_marks,status,assessment_date\n"
        b"A001,CS301,QUIZ,Imported quiz,10,9,GRADED,2026-09-06\n"
        b"A001,CS301,QUIZ,Bad,10,12,GRADED,2026-09-07\n"
    )
    assess_dry = auth_client.post(
        "/api/v1/imports/assessments?dry_run=true",
        headers=teacher,
        files={"file": ("as.csv", assessments, "text/csv")},
    )
    assert assess_dry.json()["valid"] is False

    good_assess = (
        b"student_code,subject_code,type,name,max_marks,obtained_marks,status,assessment_date\n"
        b"A001,CS301,QUIZ,Imported quiz,10,9,GRADED,2026-09-06\n"
    )
    assess_ok = auth_client.post(
        "/api/v1/imports/assessments?dry_run=false",
        headers=teacher,
        files={"file": ("as.csv", good_assess, "text/csv")},
    )
    assert assess_ok.json()["committed"] is True
    listed_a = auth_client.get("/api/v1/assessments?student_id=me", headers=student)
    assert len(listed_a.json()) == 1
    assert date.fromisoformat(listed_a.json()[0]["assessment_date"]) == date(2026, 9, 6)
