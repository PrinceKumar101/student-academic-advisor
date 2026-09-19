from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date

from app.engines.academic_types import (
    AssessmentRow,
    AttendanceRow,
    RiskSnapshotRow,
    StudentAcademicData,
)
from app.engines.analytics import overall_attendance_percent
from app.engines.risk_config import round1
from app.engines.trend_config import TREND_CONFIG, TrendConfig
from app.models.enums import (
    AssessmentStatus,
    AssessmentType,
    RiskLevel,
    WarningSeverity,
)

RISK_RANK = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
}


@dataclass(frozen=True)
class EarlyWarning:
    code: str
    severity: WarningSeverity
    message: str
    metric: str
    previous_value: float | None
    current_value: float | None


def _severity_for_drop(
    drop: float, warning_at: float, critical_at: float
) -> WarningSeverity | None:
    if drop >= critical_at:
        return WarningSeverity.CRITICAL
    if drop >= warning_at:
        return WarningSeverity.WARNING
    return None


def _window_attendance(
    rows: list[AttendanceRow], dates: list[date]
) -> float | None:
    if not dates:
        return None
    wanted = set(dates)
    held = sum(row.classes_held for row in rows if row.record_date in wanted)
    attended = sum(row.classes_attended for row in rows if row.record_date in wanted)
    if held <= 0:
        return None
    return attended / held * 100.0


def _attendance_drop_warning(
    rows: list[AttendanceRow],
    config: TrendConfig,
) -> EarlyWarning | None:
    by_date: dict[date, list[AttendanceRow]] = defaultdict(list)
    for row in rows:
        by_date[row.record_date].append(row)
    week_dates = sorted(by_date)
    recent_n = config.recent_attendance_weeks
    if len(week_dates) <= recent_n:
        return None
    recent_dates = week_dates[-recent_n:]
    previous_dates = week_dates[:-recent_n]
    previous = _window_attendance(rows, previous_dates)
    current = _window_attendance(rows, recent_dates)
    if previous is None or current is None:
        return None
    drop = previous - current
    severity = _severity_for_drop(
        drop, config.attendance_drop_warning, config.attendance_drop_critical
    )
    if severity is None:
        return None
    return EarlyWarning(
        code="ATTENDANCE_DROP",
        severity=severity,
        message=(
            f"Attendance dropped from {round1(previous)}% to {round1(current)}% "
            f"over the last {recent_n} weeks."
        ),
        metric="attendance_percent",
        previous_value=round1(previous),
        current_value=round1(current),
    )


def _marks_drop_warning(
    rows: list[AssessmentRow],
    *,
    types: tuple[AssessmentType, ...],
    code: str,
    metric: str,
    label: str,
    config: TrendConfig,
) -> EarlyWarning | None:
    graded = [
        row
        for row in rows
        if row.type in types
        and row.status is AssessmentStatus.GRADED
        and row.obtained_marks is not None
        and row.max_marks > 0
    ]
    graded.sort(key=lambda row: (row.assessment_date, row.name))
    if len(graded) < 2:
        return None
    percents = [
        row.obtained_marks / row.max_marks * 100.0 for row in graded
    ]
    previous = sum(percents[:-1]) / (len(percents) - 1)
    current = percents[-1]
    drop = previous - current
    severity = _severity_for_drop(
        drop, config.marks_drop_warning, config.marks_drop_critical
    )
    if severity is None:
        return None
    return EarlyWarning(
        code=code,
        severity=severity,
        message=(
            f"{label} dropped from {round1(previous)} to {round1(current)} "
            "(latest versus the mean of earlier scores)."
        ),
        metric=metric,
        previous_value=round1(previous),
        current_value=round1(current),
    )


def _attendance_floor_warning(
    rows: list[AttendanceRow],
    config: TrendConfig,
) -> EarlyWarning | None:
    current = overall_attendance_percent(rows)
    if current is None or current >= config.attendance_floor_warning:
        return None
    return EarlyWarning(
        code="ATTENDANCE_BELOW_FLOOR",
        severity=WarningSeverity.WARNING,
        message=(
            f"Overall attendance is {round1(current)}%, below "
            f"{round1(config.attendance_floor_warning)}%."
        ),
        metric="attendance_percent",
        previous_value=None,
        current_value=round1(current),
    )


def _missing_assignment_warning(
    rows: list[AssessmentRow],
    config: TrendConfig,
) -> EarlyWarning | None:
    assignments = [
        row for row in rows if row.type is AssessmentType.ASSIGNMENT
    ]
    assignments.sort(key=lambda row: (row.assessment_date, row.name))
    streak = 0
    for row in reversed(assignments):
        if row.status is AssessmentStatus.MISSING:
            streak += 1
            continue
        break
    if streak < config.missing_assignment_warning:
        return None
    severity = (
        WarningSeverity.CRITICAL
        if streak >= config.missing_assignment_critical
        else WarningSeverity.WARNING
    )
    return EarlyWarning(
        code="MISSING_ASSIGNMENTS",
        severity=severity,
        message=f"{streak} consecutive missing assignment(s).",
        metric="missing_assignment_streak",
        previous_value=None,
        current_value=float(streak),
    )


def _risk_increase_warning(snapshots: list[RiskSnapshotRow]) -> EarlyWarning | None:
    usable = [row for row in snapshots if row.level in RISK_RANK]
    usable.sort(key=lambda row: row.as_of)
    if len(usable) < 2:
        return None
    previous = usable[-2].level
    current = usable[-1].level
    if RISK_RANK[current] <= RISK_RANK[previous]:
        return None
    severity = (
        WarningSeverity.CRITICAL
        if previous is RiskLevel.LOW and current is RiskLevel.HIGH
        else WarningSeverity.WARNING
    )
    return EarlyWarning(
        code="RISK_LEVEL_INCREASE",
        severity=severity,
        message=f"Risk level moved from {previous.value} to {current.value}.",
        metric="risk_level",
        previous_value=float(RISK_RANK[previous]),
        current_value=float(RISK_RANK[current]),
    )


def detect_warnings(
    data: StudentAcademicData,
    snapshots: list[RiskSnapshotRow],
    config: TrendConfig | None = None,
) -> list[EarlyWarning]:
    cfg = config or TREND_CONFIG
    found: list[EarlyWarning] = []
    rules = (
        _attendance_drop_warning(data.attendance, cfg),
        _marks_drop_warning(
            data.assessments,
            types=(AssessmentType.INTERNAL, AssessmentType.EXAM),
            code="INTERNAL_DROP",
            metric="internal_percent",
            label="Internal marks",
            config=cfg,
        ),
        _marks_drop_warning(
            data.assessments,
            types=(AssessmentType.QUIZ,),
            code="QUIZ_DROP",
            metric="quiz_percent",
            label="Quiz scores",
            config=cfg,
        ),
        _attendance_floor_warning(data.attendance, cfg),
        _missing_assignment_warning(data.assessments, cfg),
        _risk_increase_warning(snapshots),
    )
    for warning in rules:
        if warning is not None:
            found.append(warning)
    return found
