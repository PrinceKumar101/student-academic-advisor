from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

from app.engines.metrics import RiskInputs, validate_risk_inputs
from app.engines.risk_config import CONFIG, RiskConfig, RiskValidationError, round1
from app.engines.risk_engine import RiskResult, compute_risk

ALLOWED_OVERRIDE_KEYS = (
    "attendance_percent",
    "internal_percent",
    "quiz_percent",
    "assignment_percent",
    "assignment_submission_rate",
    "study_hours_per_day",
    "self_confidence",
)

OVERRIDE_TO_COMPONENT = {
    "attendance_percent": "attendance",
    "internal_percent": "internal",
    "quiz_percent": "quizzes",
    "assignment_percent": "assignments",
    "assignment_submission_rate": "assignments",
    "study_hours_per_day": "study_habits",
    "self_confidence": "study_habits",
}

PERCENT_OVERRIDE_KEYS = {
    "attendance_percent",
    "internal_percent",
    "quiz_percent",
    "assignment_percent",
    "assignment_submission_rate",
}


@dataclass(frozen=True)
class ChangedFactor:
    key: str
    from_value: float | None
    to_value: float | None
    risk_from: float | None
    risk_to: float | None
    contribution_delta: float | None
    hypothetical: bool


@dataclass(frozen=True)
class SimulationResult:
    current: RiskResult
    simulated: RiskResult
    difference: float | None
    changed_factors: tuple[ChangedFactor, ...]


def _validate_overrides(overrides: dict[str, float | int]) -> None:
    unknown = sorted(set(overrides) - set(ALLOWED_OVERRIDE_KEYS))
    if unknown:
        raise RiskValidationError(f"unknown override keys: {', '.join(unknown)}")
    for key, value in overrides.items():
        if key in PERCENT_OVERRIDE_KEYS:
            if value < 0 or value > 100:
                raise RiskValidationError(f"{key} must be between 0 and 100")
        elif key == "study_hours_per_day":
            if value < 0 or value > 24:
                raise RiskValidationError(
                    "study_hours_per_day must be between 0 and 24"
                )
        elif key == "self_confidence":
            if int(value) != value or not 1 <= int(value) <= 5:
                raise RiskValidationError(
                    "self_confidence must be an integer between 1 and 5"
                )


def _applied_overrides(overrides: dict[str, float | int]) -> dict[str, float | int]:
    applied: dict[str, float | int] = {}
    for key, value in overrides.items():
        if key == "self_confidence":
            applied[key] = int(value)
        else:
            applied[key] = float(value)
    return applied


def _component_map(result: RiskResult) -> dict[str, object]:
    return {item.key: item for item in result.components}


def _value_for_component(inputs: RiskInputs, component: str) -> float | None:
    if component == "attendance":
        return inputs.attendance_percent
    if component == "internal":
        return inputs.internal_percent
    if component == "quizzes":
        return inputs.quiz_percent
    if component == "assignments":
        if inputs.assignment_percent is not None:
            return inputs.assignment_percent
        return inputs.assignment_submission_rate
    if component == "study_habits":
        if inputs.study_hours_per_day is not None:
            return inputs.study_hours_per_day
        if inputs.self_confidence is not None:
            return float(inputs.self_confidence)
        return None
    return None


def _contribution(item) -> float | None:
    return item.contribution


def _build_changed_factors(
    current_inputs: RiskInputs,
    simulated_inputs: RiskInputs,
    current: RiskResult,
    simulated: RiskResult,
    overrides: dict[str, float | int],
    config: RiskConfig,
) -> tuple[ChangedFactor, ...]:
    current_map = _component_map(current)
    simulated_map = _component_map(simulated)
    affected = {OVERRIDE_TO_COMPONENT[key] for key in overrides}
    factors: list[ChangedFactor] = []
    for key in config.weights:
        if key not in affected:
            continue
        before = current_map[key]
        after = simulated_map[key]
        before_contrib = _contribution(before)
        after_contrib = _contribution(after)
        if before_contrib is None and after_contrib is None:
            delta = None
        else:
            delta = round1((after_contrib or 0.0) - (before_contrib or 0.0))
        factors.append(
            ChangedFactor(
                key=key,
                from_value=_value_for_component(current_inputs, key),
                to_value=_value_for_component(simulated_inputs, key),
                risk_from=before.risk,
                risk_to=after.risk,
                contribution_delta=delta,
                hypothetical=not before.available and after.available,
            )
        )
    return tuple(factors)


def simulate(
    inputs: RiskInputs,
    overrides: dict[str, float | int],
    as_of: date,
    config: RiskConfig | None = None,
) -> SimulationResult:
    """Recompute risk with in-memory overrides. No I/O."""
    cfg = config or CONFIG
    _validate_overrides(overrides)
    validate_risk_inputs(inputs)
    applied = _applied_overrides(overrides)
    simulated_inputs = replace(inputs, **applied) if applied else inputs
    current = compute_risk(inputs, as_of=as_of, config=cfg)
    simulated = compute_risk(simulated_inputs, as_of=as_of, config=cfg)
    if current.score is None and simulated.score is None:
        difference: float | None = 0.0
    elif current.score is None or simulated.score is None:
        difference = None
    else:
        difference = round1(simulated.score - current.score)
    return SimulationResult(
        current=current,
        simulated=simulated,
        difference=difference,
        changed_factors=_build_changed_factors(
            inputs, simulated_inputs, current, simulated, applied, cfg
        ),
    )
