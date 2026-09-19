import json
from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from tests.helpers import (
    add_assessment,
    add_student,
    add_subject,
    add_teacher,
    bearer,
    enroll,
)

from app.ai.client import AIClientError, FakeAIClient, get_ai_client
from app.core.config import get_settings


def _today() -> date:
    return date.today()


def _exam(days: int) -> str:
    return (_today() + timedelta(days=days)).isoformat()


def _world(db_session: Session, demo_password_hash: str):
    _ua, student_a = add_student(
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
    add_teacher(db_session, password_hash=demo_password_hash, email="t@demo.edu")
    weak = add_subject(db_session, code="CS301", name="DSA")
    strong = add_subject(db_session, code="CS302", name="OS")
    other = add_subject(db_session, code="CS303", name="CN")
    enroll_weak = enroll(db_session, student_a, weak)
    enroll_strong = enroll(db_session, student_a, strong)
    add_assessment(
        db_session,
        enroll_weak,
        assessment_date=_today(),
        obtained_marks=3,
        max_marks=10,
    )
    add_assessment(
        db_session,
        enroll_strong,
        assessment_date=_today(),
        obtained_marks=9,
        max_marks=10,
    )
    return student_a, weak, strong, other


def _override(auth_app, client: FakeAIClient) -> None:
    auth_app.dependency_overrides[get_ai_client] = lambda: client


def _valid_plan_json(slot_ids: list[str], topic: str = "Trees") -> str:
    return json.dumps(
        {
            "slots": [
                {
                    "slot_id": slot_id,
                    "topic": topic,
                    "activity": f"Practice {topic}",
                }
                for slot_id in slot_ids
            ],
            "tips": ["Sleep well."],
        }
    )


def test_create_list_get_toggle_delete_and_auth(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    _student_a, weak, _strong, other = _world(db_session, demo_password_hash)
    fake = FakeAIClient(
        text=_valid_plan_json(["s1"], topic="Trees"),
    )
    _override(auth_app, fake)
    a = bearer(auth_client, "a@demo.edu")
    b = bearer(auth_client, "b@demo.edu")
    teacher = bearer(auth_client, "t@demo.edu")

    created = auth_client.post(
        "/api/v1/study-plans",
        json={
            "exam_date": _exam(1),
            "available_hours_per_day": 2,
            "subject_ids": [weak.id],
            "topics": {str(weak.id): ["Trees"]},
        },
        headers=a,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["source"] == "AI"
    assert body["items"]
    assert body["items"][0]["duration_minutes"] <= 120
    assert body["items"][0]["subject"]["code"] == "CS301"
    assert body["tips"] == ["Sleep well."]
    plan_id = body["id"]
    item_id = body["items"][0]["id"]

    listed = auth_client.get("/api/v1/study-plans", headers=a)
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == plan_id

    hidden = auth_client.get(f"/api/v1/study-plans/{plan_id}", headers=b)
    assert hidden.status_code == 403

    teacher_denied = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _exam(2), "available_hours_per_day": 2},
        headers=teacher,
    )
    assert teacher_denied.status_code == 403

    patched = auth_client.patch(
        f"/api/v1/study-plans/{plan_id}/items/{item_id}",
        json={"is_completed": True},
        headers=a,
    )
    assert patched.status_code == 200
    assert patched.json()["is_completed"] is True
    assert patched.json()["completed_at"] is not None

    again = auth_client.get(f"/api/v1/study-plans/{plan_id}", headers=a)
    assert again.json()["items"][0]["is_completed"] is True

    foreign_subject = auth_client.post(
        "/api/v1/study-plans",
        json={
            "exam_date": _exam(2),
            "available_hours_per_day": 2,
            "subject_ids": [other.id],
        },
        headers=a,
    )
    assert foreign_subject.status_code == 422

    deleted = auth_client.delete(f"/api/v1/study-plans/{plan_id}", headers=a)
    assert deleted.status_code == 204
    missing = auth_client.get(f"/api/v1/study-plans/{plan_id}", headers=a)
    assert missing.status_code == 404


def test_invalid_dates_hours_and_fallback(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    _student_a, weak, _strong, _other = _world(db_session, demo_password_hash)
    a = bearer(auth_client, "a@demo.edu")
    _override(auth_app, FakeAIClient(text="{}"))

    hours = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _exam(2), "available_hours_per_day": 13},
        headers=a,
    )
    assert hours.status_code == 422

    past = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _today().isoformat(), "available_hours_per_day": 2},
        headers=a,
    )
    assert past.status_code == 422

    far = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _exam(61), "available_hours_per_day": 2},
        headers=a,
    )
    assert far.status_code == 422

    _override(
        auth_app,
        FakeAIClient(error=AIClientError("NOT_CONFIGURED", "no key", retryable=False)),
    )
    fallback = auth_client.post(
        "/api/v1/study-plans",
        json={
            "exam_date": _exam(1),
            "available_hours_per_day": 1,
            "subject_ids": [weak.id],
        },
        headers=a,
    )
    assert fallback.status_code == 200
    assert fallback.json()["source"] == "FALLBACK"
    assert fallback.json()["fallback_reason"] == "NOT_CONFIGURED"
    assert "Revise notes and solve 5 practice questions" in fallback.json()["items"][0][
        "activity"
    ]

    _override(
        auth_app,
        FakeAIClient(
            text=json.dumps(
                {"slots": [{"slot_id": "nope", "topic": "X", "activity": "Y"}]}
            )
        ),
    )
    unknown = auth_client.post(
        "/api/v1/study-plans",
        json={
            "exam_date": _exam(1),
            "available_hours_per_day": 1,
            "subject_ids": [weak.id],
        },
        headers=a,
    )
    assert unknown.status_code == 200
    assert unknown.json()["source"] == "FALLBACK"
    assert unknown.json()["fallback_reason"] == "INVALID_OUTPUT"


def test_auto_pick_and_daily_limit(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
    monkeypatch,
) -> None:
    _student_a, weak, _strong, _other = _world(db_session, demo_password_hash)
    settings = get_settings()
    monkeypatch.setattr(settings, "ai_daily_plan_limit", 1)
    _override(
        auth_app,
        FakeAIClient(
            error=AIClientError("NOT_CONFIGURED", "no key", retryable=False)
        ),
    )
    a = bearer(auth_client, "a@demo.edu")
    first = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _exam(2), "available_hours_per_day": 2},
        headers=a,
    )
    assert first.status_code == 200
    codes = {item["subject"]["code"] for item in first.json()["items"]}
    assert codes == {"CS301"}

    second = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _exam(2), "available_hours_per_day": 2},
        headers=a,
    )
    assert second.status_code == 429
    usage = auth_client.get("/api/v1/ai/usage", headers=a)
    assert usage.json()["plans"]["used"] == 1
    assert usage.json()["plans"]["remaining"] == 0


def test_auto_pick_lowest_when_no_weak_subjects(
    auth_app,
    auth_client: TestClient,
    db_session: Session,
    demo_password_hash: str,
) -> None:
    _user, student = add_student(
        db_session,
        password_hash=demo_password_hash,
        email="good@demo.edu",
        student_code="G001",
    )
    first = add_subject(db_session, code="CS304", name="DBMS")
    second = add_subject(db_session, code="CS305", name="SE")
    enroll_first = enroll(db_session, student, first)
    enroll_second = enroll(db_session, student, second)
    add_assessment(
        db_session,
        enroll_first,
        assessment_date=_today(),
        obtained_marks=8,
        max_marks=10,
    )
    add_assessment(
        db_session,
        enroll_second,
        assessment_date=_today(),
        obtained_marks=9.5,
        max_marks=10,
    )
    _override(
        auth_app,
        FakeAIClient(error=AIClientError("NOT_CONFIGURED", "no key", retryable=False)),
    )
    headers = bearer(auth_client, "good@demo.edu")
    response = auth_client.post(
        "/api/v1/study-plans",
        json={"exam_date": _exam(1), "available_hours_per_day": 2},
        headers=headers,
    )
    assert response.status_code == 200
    codes = {item["subject"]["code"] for item in response.json()["items"]}
    assert "CS304" in codes
