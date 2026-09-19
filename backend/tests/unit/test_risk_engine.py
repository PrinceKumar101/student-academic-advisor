from copy import deepcopy
from datetime import date
from random import Random

import pytest

from app.engines.metrics import RiskInputs
from app.engines.risk_config import CONFIG, RiskValidationError
from app.engines.risk_engine import attendance_risk, classify_score, compute_risk
from app.models.enums import RiskLevel

AS_OF = date(2026, 9, 19)


def _risks(result) -> dict[str, float | None]:
    return {item.key: item.risk for item in result.components}


def test_r1_low() -> None:
    result = compute_risk(
        RiskInputs(
            attendance_percent=92,
            internal_percent=82,
            assignment_percent=85,
            assignment_submission_rate=100,
            quiz_percent=80,
            previous_percentage=78,
            study_hours_per_day=3,
            self_confidence=4,
            n_internal=2,
            n_quiz=2,
            n_assignment=2,
        ),
        as_of=AS_OF,
    )
    assert _risks(result) == {
        "attendance": 0.0,
        "internal": 0.0,
        "assignments": 0.0,
        "quizzes": 0.0,
        "previous": 0.0,
        "study_habits": 12.5,
    }
    assert result.score == 1.3
    assert result.level is RiskLevel.LOW
    assert result.escalated is False


def test_r2_medium() -> None:
    result = compute_risk(
        RiskInputs(
            attendance_percent=75,
            internal_percent=60,
            assignment_percent=65,
            assignment_submission_rate=100,
            quiz_percent=55,
            previous_percentage=65,
            study_hours_per_day=1.5,
            self_confidence=3,
            n_internal=2,
            n_quiz=2,
            n_assignment=2,
        ),
        as_of=AS_OF,
    )
    assert _risks(result) == {
        "attendance": 37.5,
        "internal": 37.5,
        "assignments": 12.5,
        "quizzes": 50.0,
        "previous": 25.0,
        "study_habits": 37.5,
    }
    assert result.score == 34.4
    assert result.level is RiskLevel.MEDIUM


def test_r3_high() -> None:
    result = compute_risk(
        RiskInputs(
            attendance_percent=64,
            internal_percent=45,
            assignment_percent=50,
            assignment_submission_rate=60,
            quiz_percent=40,
            previous_percentage=55,
            study_hours_per_day=1,
            self_confidence=2,
            n_internal=2,
            n_quiz=1,
            n_assignment=2,
        ),
        as_of=AS_OF,
    )
    assert _risks(result) == {
        "attendance": 65.0,
        "internal": 75.0,
        "assignments": 51.25,
        "quizzes": 87.5,
        "previous": 50.0,
        "study_habits": 62.5,
    }
    assert result.score == 67.1
    assert result.level is RiskLevel.HIGH
    assert result.top_factors == ("internal", "attendance", "quizzes")
    attendance = next(item for item in result.components if item.key == "attendance")
    assert attendance.note == "Attendance is 64.0%, below the 75% cutoff."
    assert attendance.contribution == 16.25
    assert "LOW_SAMPLE:quizzes" in result.flags


def test_r4_boundaries() -> None:
    assert classify_score(30.0, CONFIG) is RiskLevel.LOW
    assert classify_score(30.1, CONFIG) is RiskLevel.MEDIUM
    assert classify_score(60.0, CONFIG) is RiskLevel.MEDIUM
    assert classify_score(60.1, CONFIG) is RiskLevel.HIGH


def test_r5_missing_data_renormalizes() -> None:
    result = compute_risk(
        RiskInputs(attendance_percent=64, internal_percent=45, n_internal=2),
        as_of=AS_OF,
    )
    assert result.data_completeness == 0.50
    assert result.score == 70.0
    assert result.level is RiskLevel.HIGH
    assert "PARTIAL_DATA" in result.flags


def test_r6_insufficient_data() -> None:
    result = compute_risk(
        RiskInputs(study_hours_per_day=3, self_confidence=4),
        as_of=AS_OF,
    )
    assert result.data_completeness == 0.10
    assert result.score is None
    assert result.level is RiskLevel.INSUFFICIENT_DATA


def test_r7_escalation_floor() -> None:
    result = compute_risk(
        RiskInputs(
            attendance_percent=60,
            internal_percent=80,
            assignment_percent=80,
            assignment_submission_rate=100,
            quiz_percent=80,
            previous_percentage=80,
            study_hours_per_day=2,
            self_confidence=5,
            n_internal=2,
            n_quiz=2,
            n_assignment=2,
        ),
        as_of=AS_OF,
    )
    assert _risks(result)["attendance"] == 75.0
    assert result.score == 18.8
    assert result.level is RiskLevel.MEDIUM
    assert result.escalated is True
    assert result.escalation_reason == "Attendance below 75% cutoff"


def test_r9_clamp() -> None:
    assert attendance_risk(100, CONFIG) == 0.0
    assert attendance_risk(30, CONFIG) == 100.0


def test_r10_invalid_percent() -> None:
    with pytest.raises(RiskValidationError):
        compute_risk(RiskInputs(attendance_percent=101), as_of=AS_OF)
    with pytest.raises(RiskValidationError):
        compute_risk(RiskInputs(internal_percent=-1), as_of=AS_OF)


def test_r12_determinism_and_no_mutation() -> None:
    inputs = RiskInputs(
        attendance_percent=64,
        internal_percent=45,
        assignment_percent=50,
        assignment_submission_rate=60,
        quiz_percent=40,
        previous_percentage=55,
        study_hours_per_day=1,
        self_confidence=2,
    )
    before = deepcopy(inputs)
    first = compute_risk(inputs, as_of=AS_OF)
    second = compute_risk(inputs, as_of=AS_OF)
    assert first == second
    assert inputs == before


def test_r13_monotonic_improvement() -> None:
    rng = Random(42)
    fields = (
        "attendance_percent",
        "internal_percent",
        "quiz_percent",
        "assignment_percent",
        "assignment_submission_rate",
        "previous_percentage",
        "study_hours_per_day",
        "self_confidence",
    )
    checked = 0
    while checked < 500:
        raw = {
            "attendance_percent": rng.uniform(40, 100),
            "internal_percent": rng.uniform(30, 100),
            "quiz_percent": rng.uniform(30, 100),
            "assignment_percent": rng.uniform(30, 100),
            "assignment_submission_rate": rng.uniform(40, 100),
            "previous_percentage": rng.uniform(30, 100),
            "study_hours_per_day": rng.uniform(0.2, 5.0),
            "self_confidence": rng.randint(1, 5),
        }
        base = compute_risk(RiskInputs(**raw), as_of=AS_OF)
        if base.score is None:
            continue
        field = fields[checked % len(fields)]
        improved = dict(raw)
        if field == "self_confidence":
            if raw[field] >= 5:
                continue
            improved[field] = raw[field] + 1
        elif field == "study_hours_per_day":
            improved[field] = raw[field] + 0.5
        else:
            improved[field] = min(100.0, raw[field] + 5.0)
        better = compute_risk(RiskInputs(**improved), as_of=AS_OF)
        assert better.score is not None
        assert better.score <= base.score
        checked += 1


def test_stale_and_assignment_single_part() -> None:
    only_rate = compute_risk(
        RiskInputs(
            attendance_percent=90,
            internal_percent=80,
            assignment_submission_rate=40,
            quiz_percent=80,
            previous_percentage=80,
            n_internal=2,
            n_quiz=2,
        ),
        as_of=AS_OF,
    )
    assign = next(item for item in only_rate.components if item.key == "assignments")
    assert assign.risk == 60.0

    stale = compute_risk(
        RiskInputs(
            attendance_percent=90,
            internal_percent=80,
            n_internal=2,
            newest_record_date=date(2026, 8, 1),
        ),
        as_of=AS_OF,
    )
    assert "STALE_DATA" in stale.flags
