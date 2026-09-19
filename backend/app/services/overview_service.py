from datetime import date

from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.students import (
    OverviewRiskOut,
    OverviewTrendSummaryOut,
    StudentOverviewOut,
)
from app.services import (
    analytics_service,
    intervention_service,
    risk_service,
    student_service,
)
from app.services.trend_service import get_trends, get_warnings


def get_overview(db: Session, student: Student, as_of: date) -> StudentOverviewOut:
    profile = student_service.get_profile(student)
    risk = risk_service.get_current(db, student, as_of)
    subjects = analytics_service.get_subject_analysis(db, student, as_of)
    trends = get_trends(db, student, as_of)
    warnings = get_warnings(db, student, as_of)
    open_interventions = intervention_service.list_open_for_student(db, student.id)
    return StudentOverviewOut(
        student_id=student.id,
        as_of=as_of,
        profile=profile,
        risk=OverviewRiskOut(
            score=risk.score,
            level=risk.level,
            escalated=risk.escalated,
            escalation_reason=risk.escalation_reason,
            data_completeness=risk.data_completeness,
            config_version=risk.config_version,
            flags=list(risk.flags),
        ),
        top_factors=list(risk.top_factors),
        subjects=list(subjects.subjects),
        trend_summary=OverviewTrendSummaryOut(
            overall_label=trends.overall.label,
            overall_slope=trends.overall.slope,
            attendance_label=trends.attendance.label,
            attendance_slope=trends.attendance.slope,
        ),
        warnings=list(warnings.warnings),
        open_interventions=open_interventions,
    )
