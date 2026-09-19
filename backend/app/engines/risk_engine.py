from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date, timedelta

from app.engines.metrics import RiskInputs, validate_risk_inputs
from app.engines.risk_config import CONFIG, RiskConfig, round1
from app.models.enums import RiskLevel

COMPONENT_LABELS = {
    "attendance": "Attendance",
    "internal": "Internal",
    "assignments": "Assignments",
    "quizzes": "Quizzes",
    "previous": "Previous semester",
    "study_habits": "Study habits",
}

LEVEL_ORDER = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
}


@dataclass(frozen=True)
class ComponentResult:
    key: str
    label: str
    available: bool
    raw_value: float | None
    unit: str | None
    risk: float | None
    weight: float
    effective_weight: float | None
    contribution: float | None
    level: str | None
    note: str | None


@dataclass(frozen=True)
class RiskResult:
    score: float | None
    level: RiskLevel
    escalated: bool
    escalation_reason: str | None
    data_completeness: float
    config_version: str
    components: tuple[ComponentResult, ...]
    top_factors: tuple[str, ...]
    flags: tuple[str, ...]

    def components_payload(self) -> list[dict]:
        return [asdict(component) for component in self.components]


def clamp(value: float) -> float:
    return max(0.0, min(100.0, value))


def attendance_risk(percent: float, config: RiskConfig) -> float:
    span = config.attendance_good - config.attendance_bad
    return clamp((config.attendance_good - percent) / span * 100.0)


def performance_risk(percent: float, config: RiskConfig) -> float:
    span = config.performance_good - config.performance_bad
    return clamp((config.performance_good - percent) / span * 100.0)


def assignment_risk(
    submission_rate: float | None,
    assignment_percent: float | None,
    config: RiskConfig,
) -> float | None:
    parts: list[float] = []
    if submission_rate is not None:
        parts.append(100.0 - submission_rate)
    if assignment_percent is not None:
        parts.append(performance_risk(assignment_percent, config))
    if not parts:
        return None
    return sum(parts) / len(parts)


def study_risk(
    hours: float | None, confidence: int | None, config: RiskConfig
) -> float | None:
    parts: list[float] = []
    if hours is not None:
        hours_risk = (config.study_hours_target - hours) / config.study_hours_target
        parts.append(clamp(hours_risk * 100.0))
    if confidence is not None:
        span = config.confidence_max - config.confidence_min
        parts.append((config.confidence_max - confidence) / span * 100.0)
    if not parts:
        return None
    return sum(parts) / len(parts)


def classify_score(score: float, config: RiskConfig) -> RiskLevel:
    if score <= config.low_max:
        return RiskLevel.LOW
    if score <= config.medium_max:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH


def classify_component(risk: float, config: RiskConfig) -> RiskLevel:
    return classify_score(risk, config)


def _fmt(value: float) -> str:
    return f"{value:.1f}"


def _attendance_note(raw: float, config: RiskConfig) -> str:
    if raw < config.attendance_floor_percent:
        return (
            f"Attendance is {_fmt(raw)}%, below the "
            f"{_fmt(config.attendance_floor_percent).rstrip('0').rstrip('.')}% cutoff."
        )
    return f"Attendance is {_fmt(raw)}%."


def _internal_note(raw: float, config: RiskConfig) -> str:
    if raw < config.internal_pass_percent:
        return (
            f"Internal marks are {_fmt(raw)}%, below the "
            f"{_fmt(config.internal_pass_percent).rstrip('0').rstrip('.')}"
            "% pass cutoff."
        )
    return f"Internal marks are {_fmt(raw)}%."


def _assignment_note(
    submission_rate: float | None, assignment_percent: float | None
) -> str:
    parts: list[str] = []
    if submission_rate is not None:
        parts.append(f"assignment submission rate is {_fmt(submission_rate)}%")
    if assignment_percent is not None:
        parts.append(f"assignment marks are {_fmt(assignment_percent)}%")
    if not parts:
        return "Assignment data is available."
    text = " and ".join(parts)
    return text[0].upper() + text[1:] + "."


def _component_note(key: str, inputs: RiskInputs, config: RiskConfig) -> str | None:
    if key == "attendance" and inputs.attendance_percent is not None:
        return _attendance_note(inputs.attendance_percent, config)
    if key == "internal" and inputs.internal_percent is not None:
        return _internal_note(inputs.internal_percent, config)
    if key == "quizzes" and inputs.quiz_percent is not None:
        return f"Quiz average is {_fmt(inputs.quiz_percent)}%."
    if key == "assignments":
        if (
            inputs.assignment_percent is None
            and inputs.assignment_submission_rate is None
        ):
            return None
        return _assignment_note(
            inputs.assignment_submission_rate, inputs.assignment_percent
        )
    if key == "previous" and inputs.previous_percentage is not None:
        return f"Previous semester percentage is {_fmt(inputs.previous_percentage)}%."
    if key == "study_habits":
        bits: list[str] = []
        if inputs.study_hours_per_day is not None:
            bits.append(f"{_fmt(inputs.study_hours_per_day)} hours/day")
        if inputs.self_confidence is not None:
            bits.append(f"confidence {inputs.self_confidence}")
        if not bits:
            return None
        return "Study habits are " + " and ".join(bits) + "."
    return None


def _raw_and_unit(
    key: str, inputs: RiskInputs
) -> tuple[float | None, str | None]:
    if key == "attendance":
        return inputs.attendance_percent, "percent"
    if key == "internal":
        return inputs.internal_percent, "percent"
    if key == "quizzes":
        return inputs.quiz_percent, "percent"
    if key == "assignments":
        if inputs.assignment_percent is not None:
            return inputs.assignment_percent, "percent"
        if inputs.assignment_submission_rate is not None:
            return inputs.assignment_submission_rate, "percent"
        return None, "percent"
    if key == "previous":
        return inputs.previous_percentage, "percent"
    if key == "study_habits":
        if inputs.study_hours_per_day is not None:
            return inputs.study_hours_per_day, "hours"
        if inputs.self_confidence is not None:
            return float(inputs.self_confidence), "confidence"
        return None, "hours"
    return None, None


def _component_risks(
    inputs: RiskInputs, config: RiskConfig
) -> dict[str, float | None]:
    return {
        "attendance": (
            attendance_risk(inputs.attendance_percent, config)
            if inputs.attendance_percent is not None
            else None
        ),
        "internal": (
            performance_risk(inputs.internal_percent, config)
            if inputs.internal_percent is not None
            else None
        ),
        "assignments": assignment_risk(
            inputs.assignment_submission_rate, inputs.assignment_percent, config
        ),
        "quizzes": (
            performance_risk(inputs.quiz_percent, config)
            if inputs.quiz_percent is not None
            else None
        ),
        "previous": (
            performance_risk(inputs.previous_percentage, config)
            if inputs.previous_percentage is not None
            else None
        ),
        "study_habits": study_risk(
            inputs.study_hours_per_day, inputs.self_confidence, config
        ),
    }


def _flags(
    inputs: RiskInputs, completeness: float, as_of: date, config: RiskConfig
) -> list[str]:
    flags: list[str] = []
    samples = (
        ("internal", inputs.n_internal, inputs.internal_percent is not None),
        ("quizzes", inputs.n_quiz, inputs.quiz_percent is not None),
        ("assignments", inputs.n_assignment, inputs.assignment_percent is not None),
    )
    for key, count, available in samples:
        if available and count < config.low_sample_min:
            flags.append(f"LOW_SAMPLE:{key}")
    if completeness < 1.0:
        flags.append("PARTIAL_DATA")
    if inputs.newest_record_date is not None:
        cutoff = as_of - timedelta(days=config.stale_days)
        if inputs.newest_record_date < cutoff:
            flags.append("STALE_DATA")
    return flags


def compute_risk(
    inputs: RiskInputs,
    as_of: date,
    config: RiskConfig | None = None,
) -> RiskResult:
    cfg = config or CONFIG
    validate_risk_inputs(inputs)

    risks = _component_risks(inputs, cfg)
    available = {key: risk for key, risk in risks.items() if risk is not None}
    completeness = sum(cfg.weights[key] for key in available)

    if completeness < cfg.insufficient_weight:
        components = tuple(
            _build_component(
                key, inputs, risks[key], cfg.weights[key], None, None, cfg
            )
            for key in cfg.weights
        )
        return RiskResult(
            score=None,
            level=RiskLevel.INSUFFICIENT_DATA,
            escalated=False,
            escalation_reason=None,
            data_completeness=completeness,
            config_version=cfg.version,
            components=components,
            top_factors=(),
            flags=tuple(_flags(inputs, completeness, as_of, cfg)),
        )

    score = round1(
        sum(cfg.weights[key] / completeness * risk for key, risk in available.items())
    )
    base_level = classify_score(score, cfg)

    floor_reasons: list[str] = []
    floor_level = RiskLevel.LOW
    if (
        inputs.attendance_percent is not None
        and inputs.attendance_percent < cfg.attendance_floor_percent
    ):
        floor_level = RiskLevel.MEDIUM
        floor_reasons.append("Attendance below 75% cutoff")
    if (
        inputs.internal_percent is not None
        and inputs.internal_percent < cfg.internal_pass_percent
    ):
        floor_level = RiskLevel.MEDIUM
        floor_reasons.append("Internal marks below 40% pass cutoff")

    final_level = base_level
    if LEVEL_ORDER[floor_level] > LEVEL_ORDER[base_level]:
        final_level = floor_level
    raised = LEVEL_ORDER[final_level] > LEVEL_ORDER[base_level]
    escalated = bool(floor_reasons) and raised
    reason = "; ".join(floor_reasons) if escalated else None

    components_list: list[ComponentResult] = []
    for key, weight in cfg.weights.items():
        risk = risks[key]
        if risk is None:
            effective = None
            contribution = None
        else:
            effective = weight / completeness
            contribution = effective * risk
        components_list.append(
            _build_component(key, inputs, risk, weight, effective, contribution, cfg)
        )

    ranked = sorted(
        (
            component
            for component in components_list
            if component.available
            and component.level in (RiskLevel.MEDIUM.value, RiskLevel.HIGH.value)
        ),
        key=lambda item: (-(item.contribution or 0.0), item.key),
    )
    top_factors = tuple(item.key for item in ranked[: cfg.top_factors_max])

    return RiskResult(
        score=score,
        level=final_level,
        escalated=escalated,
        escalation_reason=reason,
        data_completeness=completeness,
        config_version=cfg.version,
        components=tuple(components_list),
        top_factors=top_factors,
        flags=tuple(_flags(inputs, completeness, as_of, cfg)),
    )


def _build_component(
    key: str,
    inputs: RiskInputs,
    risk: float | None,
    weight: float,
    effective_weight: float | None,
    contribution: float | None,
    config: RiskConfig,
) -> ComponentResult:
    raw, unit = _raw_and_unit(key, inputs)
    available = risk is not None
    level = classify_component(risk, config).value if available else None
    return ComponentResult(
        key=key,
        label=COMPONENT_LABELS[key],
        available=available,
        raw_value=raw,
        unit=unit,
        risk=risk,
        weight=weight,
        effective_weight=effective_weight,
        contribution=contribution,
        level=level,
        note=_component_note(key, inputs, config) if available else None,
    )
