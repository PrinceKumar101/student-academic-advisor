from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from app.models.enums import Priority

MIN_SHARE_FRACTION = 0.10
MIN_MINUTES = 15
HIGH_CONCERN_MAX = 50.0
MEDIUM_CONCERN_MAX = 65.0


@dataclass(frozen=True)
class SubjectConcern:
    subject_id: int
    subject_code: str
    percent: float | None


@dataclass(frozen=True)
class TimeSlot:
    slot_id: str
    date: date
    subject_id: int
    subject_code: str
    minutes: int
    priority: Priority


def concern_weight(percent: float | None) -> float:
    if percent is None:
        return 50.0
    return max(100.0 - percent, 1.0)


def priority_for_percent(percent: float | None) -> Priority:
    if percent is None or percent < HIGH_CONCERN_MAX:
        return Priority.HIGH
    if percent < MEDIUM_CONCERN_MAX:
        return Priority.MEDIUM
    return Priority.LOW


def daily_cap_minutes(available_hours_per_day: float) -> int:
    return int(available_hours_per_day * 60)


def _largest_remainder(values: list[float], total: int) -> list[int]:
    floored = [int(value) for value in values]
    leftover = total - sum(floored)
    order = sorted(
        range(len(values)),
        key=lambda index: values[index] - floored[index],
        reverse=True,
    )
    for index in order[: max(leftover, 0)]:
        floored[index] += 1
    return floored


def _allocate_day(
    subjects: list[SubjectConcern],
    cap: int,
) -> list[int]:
    count = len(subjects)
    weights = [concern_weight(item.percent) for item in subjects]
    if cap < count:
        ranked = sorted(
            range(count),
            key=lambda index: (-weights[index], subjects[index].subject_code),
        )
        minutes = [0] * count
        for index in ranked[:cap]:
            minutes[index] = 1
        return minutes

    min_each = min(MIN_MINUTES, max(1, cap // count))
    if min_each * count > cap:
        min_each = max(1, cap // count)
    remaining = cap - min_each * count
    weight_total = sum(weights)
    extras = [weight / weight_total * remaining for weight in weights]
    return [min_each + extra for extra in _largest_remainder(extras, remaining)]


def allocate(
    subjects: list[SubjectConcern],
    *,
    exam_date: date,
    available_hours_per_day: float,
    as_of: date,
) -> list[TimeSlot]:
    if not subjects:
        raise ValueError("at least one subject is required")
    days = (exam_date - as_of).days
    if days < 1:
        raise ValueError("exam_date must be after as_of")
    cap = daily_cap_minutes(available_hours_per_day)
    if cap < 1:
        raise ValueError("available hours must yield at least 1 minute")

    slots: list[TimeSlot] = []
    slot_number = 1
    for offset in range(days):
        plan_date = as_of + timedelta(days=offset)
        minutes = _allocate_day(subjects, cap)
        for subject, allocated in zip(subjects, minutes, strict=True):
            if allocated < 1:
                continue
            slots.append(
                TimeSlot(
                    slot_id=f"s{slot_number}",
                    date=plan_date,
                    subject_id=subject.subject_id,
                    subject_code=subject.subject_code,
                    minutes=allocated,
                    priority=priority_for_percent(subject.percent),
                )
            )
            slot_number += 1
    return slots
