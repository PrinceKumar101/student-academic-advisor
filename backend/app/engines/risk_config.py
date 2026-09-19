from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CONFIG_VERSION = "1.0"

COMPONENT_KEYS = (
    "attendance",
    "internal",
    "assignments",
    "quizzes",
    "previous",
    "study_habits",
)

WEIGHTS: dict[str, float] = {
    "attendance": 0.25,
    "internal": 0.25,
    "assignments": 0.15,
    "quizzes": 0.15,
    "previous": 0.10,
    "study_habits": 0.10,
}

ATTENDANCE_GOOD = 90.0
ATTENDANCE_BAD = 50.0
PERFORMANCE_GOOD = 75.0
PERFORMANCE_BAD = 35.0
STUDY_HOURS_TARGET = 2.0
CONFIDENCE_MIN = 1
CONFIDENCE_MAX = 5

LOW_MAX = 30.0
MEDIUM_MAX = 60.0
INSUFFICIENT_WEIGHT = 0.40

ATTENDANCE_FLOOR_PERCENT = 75.0
INTERNAL_PASS_PERCENT = 40.0

LOW_SAMPLE_MIN = 2
STALE_DAYS = 30
TOP_FACTORS_MAX = 3

WEIGHT_SUM_TOLERANCE = 1e-9


class RiskConfigError(ValueError):
    """Invalid risk configuration."""


class RiskValidationError(ValueError):
    """Invalid academic inputs for risk scoring."""


@dataclass(frozen=True)
class RiskConfig:
    version: str
    weights: dict[str, float]
    attendance_good: float
    attendance_bad: float
    performance_good: float
    performance_bad: float
    study_hours_target: float
    confidence_min: int
    confidence_max: int
    low_max: float
    medium_max: float
    insufficient_weight: float
    attendance_floor_percent: float
    internal_pass_percent: float
    low_sample_min: int
    stale_days: int
    top_factors_max: int


def round1(value: float) -> float:
    """Round half up to one decimal place."""
    quantized = Decimal(str(value)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
    return float(quantized)


def validate_config(config: RiskConfig) -> None:
    missing = [key for key in COMPONENT_KEYS if key not in config.weights]
    extra = [key for key in config.weights if key not in COMPONENT_KEYS]
    if missing or extra:
        raise RiskConfigError(
            f"Weights must include exactly {COMPONENT_KEYS}; "
            f"missing={missing} extra={extra}"
        )
    if any(weight < 0 for weight in config.weights.values()):
        raise RiskConfigError("Weights must be non-negative")
    total = sum(config.weights.values())
    if abs(total - 1.0) > WEIGHT_SUM_TOLERANCE:
        raise RiskConfigError(f"Weights must sum to 1.00, got {total}")
    if config.attendance_good <= config.attendance_bad:
        raise RiskConfigError("Attendance good point must be above the bad point")
    if config.performance_good <= config.performance_bad:
        raise RiskConfigError("Performance good point must be above the bad point")
    if config.low_max > config.medium_max:
        raise RiskConfigError("LOW cutoff must be at or below the MEDIUM cutoff")
    if not 0 < config.insufficient_weight <= 1:
        raise RiskConfigError("Insufficient-data threshold must be in (0, 1]")
    if config.study_hours_target <= 0:
        raise RiskConfigError("Study hours target must be positive")
    if config.confidence_max <= config.confidence_min:
        raise RiskConfigError("Confidence max must be above min")


def default_config() -> RiskConfig:
    return RiskConfig(
        version=CONFIG_VERSION,
        weights=dict(WEIGHTS),
        attendance_good=ATTENDANCE_GOOD,
        attendance_bad=ATTENDANCE_BAD,
        performance_good=PERFORMANCE_GOOD,
        performance_bad=PERFORMANCE_BAD,
        study_hours_target=STUDY_HOURS_TARGET,
        confidence_min=CONFIDENCE_MIN,
        confidence_max=CONFIDENCE_MAX,
        low_max=LOW_MAX,
        medium_max=MEDIUM_MAX,
        insufficient_weight=INSUFFICIENT_WEIGHT,
        attendance_floor_percent=ATTENDANCE_FLOOR_PERCENT,
        internal_pass_percent=INTERNAL_PASS_PERCENT,
        low_sample_min=LOW_SAMPLE_MIN,
        stale_days=STALE_DAYS,
        top_factors_max=TOP_FACTORS_MAX,
    )


CONFIG = default_config()
validate_config(CONFIG)
