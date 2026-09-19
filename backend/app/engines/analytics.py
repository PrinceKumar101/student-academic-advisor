from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

import pandas as pd

from app.engines.academic_types import AssessmentRow, AttendanceRow, StudentAcademicData
from app.engines.risk_config import round1
from app.engines.trend_config import TREND_CONFIG, TrendConfig
from app.models.enums import AssessmentStatus, RiskLevel, SubjectBand, TrendLabel


@dataclass(frozen=True)
class SubjectAnalysis:
    subject_id: int
    performance_percent: float | None
    band: SubjectBand | None
    attendance_percent: float | None
    attendance_alert: bool


@dataclass(frozen=True)
class StudentAnalyticsRow:
    student_id: int
    department: str
    semester: int
    section: str
    attendance_percent: float | None
    marks_percent: float | None
    risk_level: str | None
    trend_label: str | None
    risk_score: float | None = None
    subject_percents: dict[int, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ClassAnalyticsResult:
    group_size: int
    risk_counts: dict[str, int]
    mean_attendance: float | None
    mean_marks: float | None
    subject_means: dict[int, float]
    trend_distribution: dict[str, int]


@dataclass(frozen=True)
class ComparisonResult:
    available: bool
    group_size: int
    student_attendance: float | None
    student_marks: float | None
    class_attendance: float | None
    class_marks: float | None
    reason: str | None = None


def _ratio_percent(obtained: float, maximum: float) -> float | None:
    if maximum <= 0:
        return None
    return obtained / maximum * 100.0


def overall_marks_percent(rows: list[AssessmentRow]) -> float | None:
    graded = [
        row
        for row in rows
        if row.status is AssessmentStatus.GRADED and row.obtained_marks is not None
    ]
    return _ratio_percent(
        sum(row.obtained_marks for row in graded),
        sum(row.max_marks for row in graded),
    )


def overall_attendance_percent(rows: list[AttendanceRow]) -> float | None:
    held = sum(row.classes_held for row in rows)
    attended = sum(row.classes_attended for row in rows)
    return _ratio_percent(attended, held)


def subject_band(percent: float, config: TrendConfig | None = None) -> SubjectBand:
    cfg = config or TREND_CONFIG
    if percent < cfg.subject_high_concern_max:
        return SubjectBand.HIGH_CONCERN
    if percent < cfg.subject_medium_max:
        return SubjectBand.MEDIUM
    return SubjectBand.GOOD


def analyze_subjects(
    data: StudentAcademicData,
    config: TrendConfig | None = None,
) -> list[SubjectAnalysis]:
    cfg = config or TREND_CONFIG
    obtained: dict[int, float] = defaultdict(float)
    maximum: dict[int, float] = defaultdict(float)
    for row in data.assessments:
        if row.status is not AssessmentStatus.GRADED or row.obtained_marks is None:
            continue
        obtained[row.subject_id] += row.obtained_marks
        maximum[row.subject_id] += row.max_marks

    held: dict[int, int] = defaultdict(int)
    attended: dict[int, int] = defaultdict(int)
    for row in data.attendance:
        held[row.subject_id] += row.classes_held
        attended[row.subject_id] += row.classes_attended

    results: list[SubjectAnalysis] = []
    for subject_id in data.subject_ids:
        performance = _ratio_percent(obtained[subject_id], maximum[subject_id])
        attendance = _ratio_percent(attended[subject_id], held[subject_id])
        alert = (
            attendance is not None and attendance < cfg.subject_attendance_alert
        )
        results.append(
            SubjectAnalysis(
                subject_id=subject_id,
                performance_percent=(
                    round1(performance) if performance is not None else None
                ),
                band=(
                    subject_band(performance, cfg) if performance is not None else None
                ),
                attendance_percent=(
                    round1(attendance) if attendance is not None else None
                ),
                attendance_alert=alert,
            )
        )
    return results


def class_analytics(rows: list[StudentAnalyticsRow]) -> ClassAnalyticsResult:
    if not rows:
        return ClassAnalyticsResult(
            group_size=0,
            risk_counts={level.value: 0 for level in RiskLevel},
            mean_attendance=None,
            mean_marks=None,
            subject_means={},
            trend_distribution={label.value: 0 for label in TrendLabel},
        )

    frame = pd.DataFrame(
        {
            "student_id": [row.student_id for row in rows],
            "attendance": [row.attendance_percent for row in rows],
            "marks": [row.marks_percent for row in rows],
            "risk_level": [row.risk_level for row in rows],
            "trend_label": [row.trend_label for row in rows],
        }
    )
    risk_counts = {level.value: 0 for level in RiskLevel}
    for level, count in frame["risk_level"].value_counts(dropna=True).items():
        risk_counts[str(level)] = int(count)

    trend_distribution = {label.value: 0 for label in TrendLabel}
    for label, count in frame["trend_label"].value_counts(dropna=True).items():
        trend_distribution[str(label)] = int(count)

    attendance_mean = frame["attendance"].mean(skipna=True)
    marks_mean = frame["marks"].mean(skipna=True)

    subject_records: list[dict[str, float | int]] = []
    for row in rows:
        for subject_id, percent in row.subject_percents.items():
            subject_records.append({"subject_id": subject_id, "percent": percent})
    subject_means: dict[int, float] = {}
    if subject_records:
        subjects = pd.DataFrame(subject_records)
        grouped = subjects.groupby("subject_id", sort=True)["percent"].mean()
        subject_means = {
            int(subject_id): round1(float(value))
            for subject_id, value in grouped.items()
        }

    return ClassAnalyticsResult(
        group_size=len(rows),
        risk_counts=risk_counts,
        mean_attendance=(
            None if pd.isna(attendance_mean) else round1(float(attendance_mean))
        ),
        mean_marks=None if pd.isna(marks_mean) else round1(float(marks_mean)),
        subject_means=subject_means,
        trend_distribution=trend_distribution,
    )


def student_vs_class(
    student_id: int,
    rows: list[StudentAnalyticsRow],
    config: TrendConfig | None = None,
) -> ComparisonResult:
    cfg = config or TREND_CONFIG
    group_size = len(rows)
    student = next((row for row in rows if row.student_id == student_id), None)
    if group_size < cfg.comparison_min_group or student is None:
        return ComparisonResult(
            available=False,
            group_size=group_size,
            student_attendance=None,
            student_marks=None,
            class_attendance=None,
            class_marks=None,
            reason=(
                "Comparison is only shown when the group has at least "
                f"{cfg.comparison_min_group} students."
            ),
        )

    summary = class_analytics(rows)
    return ComparisonResult(
        available=True,
        group_size=group_size,
        student_attendance=(
            None
            if student.attendance_percent is None
            else round1(student.attendance_percent)
        ),
        student_marks=(
            None if student.marks_percent is None else round1(student.marks_percent)
        ),
        class_attendance=summary.mean_attendance,
        class_marks=summary.mean_marks,
    )
