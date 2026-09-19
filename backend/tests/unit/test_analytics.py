from datetime import date

from app.engines.academic_types import AssessmentRow, AttendanceRow, StudentAcademicData
from app.engines.analytics import (
    StudentAnalyticsRow,
    analyze_subjects,
    class_analytics,
    student_vs_class,
    subject_band,
)
from app.models.enums import AssessmentStatus, AssessmentType, SubjectBand, TrendLabel


def test_subject_bands_at_boundaries() -> None:
    assert subject_band(49.9) is SubjectBand.HIGH_CONCERN
    assert subject_band(50) is SubjectBand.MEDIUM
    assert subject_band(64.9) is SubjectBand.MEDIUM
    assert subject_band(65) is SubjectBand.GOOD


def test_subject_analysis_and_attendance_alert() -> None:
    data = StudentAcademicData(
        student_id=1,
        subject_ids=[1, 2],
        attendance=[
            AttendanceRow(1, date(2026, 6, 1), 10, 7),
            AttendanceRow(2, date(2026, 6, 1), 10, 9),
        ],
        assessments=[
            AssessmentRow(
                1,
                AssessmentType.INTERNAL,
                "I1",
                100,
                48,
                AssessmentStatus.GRADED,
                date(2026, 6, 2),
            ),
            AssessmentRow(
                2,
                AssessmentType.INTERNAL,
                "I1",
                100,
                80,
                AssessmentStatus.GRADED,
                date(2026, 6, 2),
            ),
        ],
    )
    results = {item.subject_id: item for item in analyze_subjects(data)}
    assert results[1].band is SubjectBand.HIGH_CONCERN
    assert results[1].performance_percent == 48.0
    assert results[1].attendance_alert is True
    assert results[2].band is SubjectBand.GOOD
    assert results[2].attendance_alert is False


def test_empty_subject_analysis() -> None:
    assert analyze_subjects(StudentAcademicData(student_id=1)) == []


def test_class_analytics_and_comparison_threshold() -> None:
    rows = [
        StudentAnalyticsRow(
            student_id=index,
            department="CSE",
            semester=5,
            section="B",
            attendance_percent=60.0 + index,
            marks_percent=50.0 + index,
            risk_level="HIGH" if index < 2 else "LOW",
            trend_label=(
                TrendLabel.DECLINING.value if index < 2 else TrendLabel.STABLE.value
            ),
            subject_percents={1: 40.0 + index},
        )
        for index in range(4)
    ]
    small = student_vs_class(1, rows)
    assert small.available is False
    assert small.group_size == 4

    rows.append(
        StudentAnalyticsRow(
            student_id=4,
            department="CSE",
            semester=5,
            section="B",
            attendance_percent=80.0,
            marks_percent=70.0,
            risk_level="MEDIUM",
            trend_label=TrendLabel.IMPROVING.value,
            subject_percents={1: 70.0},
        )
    )
    summary = class_analytics(rows)
    assert summary.group_size == 5
    assert summary.risk_counts["HIGH"] == 2
    assert summary.trend_distribution[TrendLabel.DECLINING.value] == 2
    assert summary.mean_attendance is not None
    assert 1 in summary.subject_means
    comparison = student_vs_class(1, rows)
    assert comparison.available is True
    assert comparison.student_attendance == 61.0
