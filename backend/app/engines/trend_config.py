from __future__ import annotations

from dataclasses import dataclass

from app.engines.risk_config import RiskConfigError

TREND_CONFIG_VERSION = "1.0"

MIN_POINTS = 3
SLOPE_IMPROVING = 2.0
SLOPE_DECLINING = -2.0
SUDDEN_CHANGE_POINTS = 15.0

SUBJECT_HIGH_CONCERN_MAX = 50.0
SUBJECT_MEDIUM_MAX = 65.0
SUBJECT_ATTENDANCE_ALERT = 75.0

RECENT_ATTENDANCE_WEEKS = 4
ATTENDANCE_DROP_WARNING = 10.0
ATTENDANCE_DROP_CRITICAL = 20.0
MARKS_DROP_WARNING = 10.0
MARKS_DROP_CRITICAL = 20.0
ATTENDANCE_FLOOR_WARNING = 75.0
MISSING_ASSIGNMENT_WARNING = 2
MISSING_ASSIGNMENT_CRITICAL = 3

COMPARISON_MIN_GROUP = 5


@dataclass(frozen=True)
class TrendConfig:
    version: str
    min_points: int
    slope_improving: float
    slope_declining: float
    sudden_change_points: float
    subject_high_concern_max: float
    subject_medium_max: float
    subject_attendance_alert: float
    recent_attendance_weeks: int
    attendance_drop_warning: float
    attendance_drop_critical: float
    marks_drop_warning: float
    marks_drop_critical: float
    attendance_floor_warning: float
    missing_assignment_warning: int
    missing_assignment_critical: int
    comparison_min_group: int


def validate_trend_config(config: TrendConfig) -> None:
    if config.min_points < 2:
        raise RiskConfigError("Trend min_points must be at least 2")
    if config.slope_improving < 0:
        raise RiskConfigError("Improving slope threshold must be non-negative")
    if config.slope_declining > 0:
        raise RiskConfigError("Declining slope threshold must be non-positive")
    if config.sudden_change_points <= 0:
        raise RiskConfigError("Sudden-change threshold must be positive")
    if config.subject_high_concern_max > config.subject_medium_max:
        raise RiskConfigError("Subject HIGH_CONCERN cutoff must be at or below MEDIUM")
    if config.recent_attendance_weeks < 1:
        raise RiskConfigError("Recent attendance window must be at least 1 week")
    if config.attendance_drop_warning > config.attendance_drop_critical:
        raise RiskConfigError("Attendance WARNING drop must be at or below CRITICAL")
    if config.marks_drop_warning > config.marks_drop_critical:
        raise RiskConfigError("Marks WARNING drop must be at or below CRITICAL")
    if config.missing_assignment_warning > config.missing_assignment_critical:
        raise RiskConfigError("Missing-assignment WARNING must be at or below CRITICAL")
    if config.comparison_min_group < 2:
        raise RiskConfigError("Comparison group minimum must be at least 2")


def default_trend_config() -> TrendConfig:
    return TrendConfig(
        version=TREND_CONFIG_VERSION,
        min_points=MIN_POINTS,
        slope_improving=SLOPE_IMPROVING,
        slope_declining=SLOPE_DECLINING,
        sudden_change_points=SUDDEN_CHANGE_POINTS,
        subject_high_concern_max=SUBJECT_HIGH_CONCERN_MAX,
        subject_medium_max=SUBJECT_MEDIUM_MAX,
        subject_attendance_alert=SUBJECT_ATTENDANCE_ALERT,
        recent_attendance_weeks=RECENT_ATTENDANCE_WEEKS,
        attendance_drop_warning=ATTENDANCE_DROP_WARNING,
        attendance_drop_critical=ATTENDANCE_DROP_CRITICAL,
        marks_drop_warning=MARKS_DROP_WARNING,
        marks_drop_critical=MARKS_DROP_CRITICAL,
        attendance_floor_warning=ATTENDANCE_FLOOR_WARNING,
        missing_assignment_warning=MISSING_ASSIGNMENT_WARNING,
        missing_assignment_critical=MISSING_ASSIGNMENT_CRITICAL,
        comparison_min_group=COMPARISON_MIN_GROUP,
    )


TREND_CONFIG = default_trend_config()
validate_trend_config(TREND_CONFIG)
