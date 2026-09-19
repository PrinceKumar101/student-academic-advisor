from copy import deepcopy
from datetime import date

import pytest

from app.engines.metrics import RiskInputs
from app.engines.risk_config import RiskValidationError
from app.engines.whatif import simulate
from app.models.enums import RiskLevel

AS_OF = date(2026, 9, 19)

R3 = RiskInputs(
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
)


def test_w1_attendance_64_to_80() -> None:
    original = deepcopy(R3)
    result = simulate(R3, {"attendance_percent": 80}, as_of=AS_OF)
    assert R3 == original
    assert result.current.score == 67.1
    assert result.current.level is RiskLevel.HIGH
    assert result.simulated.score == 57.1
    assert result.simulated.level is RiskLevel.MEDIUM
    assert result.difference == -10.0
    attendance = next(
        item for item in result.changed_factors if item.key == "attendance"
    )
    assert attendance.from_value == 64
    assert attendance.to_value == 80
    assert attendance.risk_from == 65.0
    assert attendance.risk_to == 25.0
    assert attendance.contribution_delta == -10.0
    assert attendance.hypothetical is False


def test_empty_overrides_difference_zero() -> None:
    result = simulate(R3, {}, as_of=AS_OF)
    assert result.difference == 0.0
    assert result.current.score == result.simulated.score
    assert result.changed_factors == ()


def test_unknown_override_key() -> None:
    with pytest.raises(RiskValidationError, match="unknown override"):
        simulate(R3, {"gpa": 9}, as_of=AS_OF)


def test_out_of_range_override() -> None:
    with pytest.raises(RiskValidationError, match="attendance_percent"):
        simulate(R3, {"attendance_percent": 120}, as_of=AS_OF)


def test_activating_none_component_is_hypothetical() -> None:
    inputs = RiskInputs(
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
    )
    result = simulate(inputs, {"attendance_percent": 80}, as_of=AS_OF)
    attendance = next(
        item for item in result.changed_factors if item.key == "attendance"
    )
    assert attendance.hypothetical is True
    assert attendance.from_value is None
    assert attendance.to_value == 80
    assert attendance.risk_from is None
    assert attendance.risk_to == 25.0
    assert result.current.score is not None
    assert result.simulated.score is not None
