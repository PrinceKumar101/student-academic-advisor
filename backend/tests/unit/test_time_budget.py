from datetime import date, timedelta

import pytest

from app.engines.time_budget import SubjectConcern, allocate, daily_cap_minutes
from app.models.enums import Priority

AS_OF = date(2026, 9, 19)


def test_daily_minutes_never_exceed_cap() -> None:
    subjects = [
        SubjectConcern(1, "CS301", 40),
        SubjectConcern(2, "CS302", 55),
        SubjectConcern(3, "CS303", 80),
    ]
    slots = allocate(
        subjects,
        exam_date=AS_OF + timedelta(days=5),
        available_hours_per_day=2.5,
        as_of=AS_OF,
    )
    cap = daily_cap_minutes(2.5)
    by_day: dict[date, int] = {}
    for slot in slots:
        by_day[slot.date] = by_day.get(slot.date, 0) + slot.minutes
    assert len(by_day) == 5
    assert all(total <= cap for total in by_day.values())
    assert all(total == cap for total in by_day.values())


def test_weaker_subject_gets_more_minutes() -> None:
    subjects = [
        SubjectConcern(1, "CS301", 35),
        SubjectConcern(2, "CS302", 90),
    ]
    slots = allocate(
        subjects,
        exam_date=AS_OF + timedelta(days=1),
        available_hours_per_day=3,
        as_of=AS_OF,
    )
    weak = sum(slot.minutes for slot in slots if slot.subject_code == "CS301")
    strong = sum(slot.minutes for slot in slots if slot.subject_code == "CS302")
    assert weak > strong
    assert {slot.priority for slot in slots if slot.subject_code == "CS301"} == {
        Priority.HIGH
    }


def test_exam_tomorrow_is_one_day() -> None:
    subjects = [SubjectConcern(1, "CS301", 50)]
    slots = allocate(
        subjects,
        exam_date=AS_OF + timedelta(days=1),
        available_hours_per_day=0.5,
        as_of=AS_OF,
    )
    assert {slot.date for slot in slots} == {AS_OF}
    assert sum(slot.minutes for slot in slots) == 30
    assert slots[0].slot_id == "s1"


def test_allocate_requires_future_exam() -> None:
    with pytest.raises(ValueError, match="exam_date"):
        allocate(
            [SubjectConcern(1, "CS301", 50)],
            exam_date=AS_OF,
            available_hours_per_day=2,
            as_of=AS_OF,
        )
