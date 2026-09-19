from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date

from app.engines.academic_types import (
    AssessmentRow,
    AttendanceRow,
    RiskSnapshotRow,
    StudentAcademicData,
)
from app.engines.risk_config import round1
from app.engines.trend_config import TREND_CONFIG, TrendConfig
from app.models.enums import AssessmentStatus, AssessmentType, SuddenChange, TrendLabel


@dataclass(frozen=True)
class SeriesPoint:
    on: date
    value: float


@dataclass(frozen=True)
class TrendResult:
    label: TrendLabel
    slope: float | None
    point_count: int
    first: float | None
    last: float | None
    mean: float | None
    sudden_change: SuddenChange | None
    points: tuple[SeriesPoint, ...] = ()


@dataclass
class StudentTrends:
    overall: TrendResult
    by_type: dict[AssessmentType, TrendResult] = field(default_factory=dict)
    by_subject: dict[int, TrendResult] = field(default_factory=dict)
    attendance: TrendResult | None = None
    risk: TrendResult | None = None


def least_squares_slope(values: list[float]) -> float:
    n = len(values)
    if n < 2:
        raise ValueError("least-squares slope needs at least two points")
    sum_x = (n - 1) * n / 2.0
    sum_y = sum(values)
    sum_xy = sum(index * value for index, value in enumerate(values))
    sum_x2 = (n - 1) * n * (2 * n - 1) / 6.0
    denominator = n * sum_x2 - sum_x * sum_x
    if denominator == 0:
        raise ValueError("least-squares slope is undefined for this series")
    return (n * sum_xy - sum_x * sum_y) / denominator


def analyze_series(
    points: list[SeriesPoint],
    config: TrendConfig | None = None,
) -> TrendResult:
    cfg = config or TREND_CONFIG
    ordered = sorted(points, key=lambda item: (item.on, item.value))
    values = [item.value for item in ordered]
    count = len(values)
    if count < cfg.min_points:
        return TrendResult(
            label=TrendLabel.INSUFFICIENT_DATA,
            slope=None,
            point_count=count,
            first=round1(values[0]) if values else None,
            last=round1(values[-1]) if values else None,
            mean=round1(sum(values) / count) if values else None,
            sudden_change=None,
            points=tuple(ordered),
        )

    slope = round1(least_squares_slope(values))
    if slope >= cfg.slope_improving:
        label = TrendLabel.IMPROVING
    elif slope <= cfg.slope_declining:
        label = TrendLabel.DECLINING
    else:
        label = TrendLabel.STABLE

    previous_mean = sum(values[:-1]) / (count - 1)
    delta = values[-1] - previous_mean
    sudden: SuddenChange | None = None
    if delta >= cfg.sudden_change_points:
        sudden = SuddenChange.SUDDEN_RISE
    elif delta <= -cfg.sudden_change_points:
        sudden = SuddenChange.SUDDEN_DROP

    return TrendResult(
        label=label,
        slope=slope,
        point_count=count,
        first=round1(values[0]),
        last=round1(values[-1]),
        mean=round1(sum(values) / count),
        sudden_change=sudden,
        points=tuple(ordered),
    )


def _graded_percent(row: AssessmentRow) -> float | None:
    if row.status is not AssessmentStatus.GRADED or row.obtained_marks is None:
        return None
    if row.max_marks <= 0:
        return None
    return row.obtained_marks / row.max_marks * 100.0


def assessment_points(
    rows: list[AssessmentRow],
    *,
    assessment_type: AssessmentType | None = None,
    subject_id: int | None = None,
) -> list[SeriesPoint]:
    points: list[SeriesPoint] = []
    for row in rows:
        if assessment_type is not None and row.type is not assessment_type:
            continue
        if subject_id is not None and row.subject_id != subject_id:
            continue
        percent = _graded_percent(row)
        if percent is None:
            continue
        points.append(SeriesPoint(on=row.assessment_date, value=percent))
    return points


def weekly_attendance_points(rows: list[AttendanceRow]) -> list[SeriesPoint]:
    held_by_date: dict[date, int] = defaultdict(int)
    attended_by_date: dict[date, int] = defaultdict(int)
    for row in rows:
        held_by_date[row.record_date] += row.classes_held
        attended_by_date[row.record_date] += row.classes_attended
    points: list[SeriesPoint] = []
    for record_date in sorted(held_by_date):
        held = held_by_date[record_date]
        if held <= 0:
            continue
        percent = attended_by_date[record_date] / held * 100.0
        points.append(SeriesPoint(on=record_date, value=percent))
    return points


def risk_points(rows: list[RiskSnapshotRow]) -> list[SeriesPoint]:
    latest_by_date: dict[date, float] = {}
    for row in rows:
        if row.score is None:
            continue
        latest_by_date[row.as_of] = row.score
    return [
        SeriesPoint(on=on, value=value)
        for on, value in sorted(latest_by_date.items())
    ]


def build_student_trends(
    data: StudentAcademicData,
    snapshots: list[RiskSnapshotRow],
    config: TrendConfig | None = None,
) -> StudentTrends:
    cfg = config or TREND_CONFIG
    overall = analyze_series(assessment_points(data.assessments), cfg)
    by_type = {
        assessment_type: analyze_series(
            assessment_points(data.assessments, assessment_type=assessment_type),
            cfg,
        )
        for assessment_type in AssessmentType
    }
    by_subject = {
        subject_id: analyze_series(
            assessment_points(data.assessments, subject_id=subject_id),
            cfg,
        )
        for subject_id in data.subject_ids
    }
    return StudentTrends(
        overall=overall,
        by_type=by_type,
        by_subject=by_subject,
        attendance=analyze_series(weekly_attendance_points(data.attendance), cfg),
        risk=analyze_series(risk_points(snapshots), cfg),
    )
