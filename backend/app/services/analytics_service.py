from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.analytics import (
    StudentAnalyticsRow,
    analyze_subjects,
    overall_attendance_percent,
    overall_marks_percent,
    student_vs_class,
)
from app.engines.metrics import to_risk_inputs
from app.engines.risk_config import RiskValidationError
from app.engines.risk_engine import compute_risk
from app.engines.trend_engine import build_student_trends
from app.models.student import Student
from app.models.subject import Subject
from app.schemas.analytics import (
    ComparisonGroupOut,
    ComparisonMetricsOut,
    ComparisonOut,
    SubjectAnalysisListOut,
    SubjectAnalysisOut,
)
from app.services.academic_data_loader import load
from app.services.trend_service import load_snapshots, load_snapshots_bulk


def build_student_analytics_rows(
    db: Session, students: list[Student], as_of: date
) -> list[StudentAnalyticsRow]:
    if not students:
        return []
    student_ids = [student.id for student in students]
    loaded = {item.student_id: item for item in load(db, student_ids, as_of)}
    snapshots_by_id = load_snapshots_bulk(db, student_ids, as_of)
    rows: list[StudentAnalyticsRow] = []
    for student in students:
        data = loaded[student.id]
        snapshots = snapshots_by_id.get(student.id, [])
        trends = build_student_trends(data, snapshots)
        subjects = analyze_subjects(data)
        try:
            risk = compute_risk(to_risk_inputs(data), as_of=as_of)
            risk_level = risk.level.value
            risk_score = risk.score
        except RiskValidationError:
            risk_level = None
            risk_score = None
        rows.append(
            StudentAnalyticsRow(
                student_id=student.id,
                department=student.department,
                semester=student.semester,
                section=student.section,
                attendance_percent=overall_attendance_percent(data.attendance),
                marks_percent=overall_marks_percent(data.assessments),
                risk_level=risk_level,
                trend_label=trends.overall.label.value,
                risk_score=risk_score,
                subject_percents={
                    item.subject_id: item.performance_percent
                    for item in subjects
                    if item.performance_percent is not None
                },
            )
        )
    return rows


def get_subject_analysis(
    db: Session, student: Student, as_of: date
) -> SubjectAnalysisListOut:
    data = load(db, [student.id], as_of)[0]
    subjects: dict[int, Subject] = {}
    if data.subject_ids:
        subjects = {
            row.id: row
            for row in db.execute(
                select(Subject).where(Subject.id.in_(data.subject_ids))
            ).scalars().all()
        }
    return SubjectAnalysisListOut(
        student_id=student.id,
        as_of=as_of,
        subjects=[
            SubjectAnalysisOut(
                subject_id=item.subject_id,
                code=subjects[item.subject_id].code,
                name=subjects[item.subject_id].name,
                performance_percent=item.performance_percent,
                band=item.band,
                attendance_percent=item.attendance_percent,
                attendance_alert=item.attendance_alert,
            )
            for item in analyze_subjects(data)
            if item.subject_id in subjects
        ],
    )


def get_comparison(db: Session, student: Student, as_of: date) -> ComparisonOut:
    peers = db.execute(
        select(Student).where(
            Student.department == student.department,
            Student.semester == student.semester,
            Student.section == student.section,
        )
    ).scalars().all()
    peer_ids = [row.id for row in peers]
    loaded = (
        {item.student_id: item for item in load(db, peer_ids, as_of)}
        if peer_ids
        else {}
    )
    rows: list[StudentAnalyticsRow] = []
    for peer in peers:
        data = loaded[peer.id]
        snapshots = load_snapshots(db, peer.id, as_of)
        trends = build_student_trends(data, snapshots)
        subjects = analyze_subjects(data)
        rows.append(
            StudentAnalyticsRow(
                student_id=peer.id,
                department=peer.department,
                semester=peer.semester,
                section=peer.section,
                attendance_percent=overall_attendance_percent(data.attendance),
                marks_percent=overall_marks_percent(data.assessments),
                risk_level=snapshots[-1].level.value if snapshots else None,
                trend_label=trends.overall.label.value,
                subject_percents={
                    item.subject_id: item.performance_percent
                    for item in subjects
                    if item.performance_percent is not None
                },
            )
        )

    result = student_vs_class(student.id, rows)
    return ComparisonOut(
        student_id=student.id,
        as_of=as_of,
        available=result.available,
        group_size=result.group_size,
        group=ComparisonGroupOut(
            department=student.department,
            semester=student.semester,
            section=student.section,
        ),
        student=(
            ComparisonMetricsOut(
                attendance_percent=result.student_attendance,
                marks_percent=result.student_marks,
            )
            if result.available
            else None
        ),
        class_average=(
            ComparisonMetricsOut(
                attendance_percent=result.class_attendance,
                marks_percent=result.class_marks,
            )
            if result.available
            else None
        ),
        reason=result.reason,
    )
