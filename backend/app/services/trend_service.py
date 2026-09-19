from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.academic_types import RiskSnapshotRow
from app.engines.trend_engine import TrendResult, build_student_trends
from app.engines.warnings import detect_warnings
from app.models.risk_assessment import RiskAssessment
from app.models.student import Student
from app.models.subject import Subject
from app.schemas.trends import (
    SubjectTrendOut,
    TrendPointOut,
    TrendSeriesOut,
    TrendsOut,
    TypedTrendOut,
    WarningOut,
    WarningsOut,
)
from app.services.academic_data_loader import load


def load_snapshots_bulk(
    db: Session, student_ids: list[int], as_of: date
) -> dict[int, list[RiskSnapshotRow]]:
    grouped: dict[int, list[RiskSnapshotRow]] = {sid: [] for sid in student_ids}
    if not student_ids:
        return grouped
    rows = db.execute(
        select(RiskAssessment)
        .where(
            RiskAssessment.student_id.in_(student_ids),
            RiskAssessment.as_of <= as_of,
        )
        .order_by(
            RiskAssessment.student_id.asc(),
            RiskAssessment.as_of.asc(),
            RiskAssessment.computed_at.asc(),
        )
    ).scalars().all()
    for row in rows:
        grouped.setdefault(row.student_id, []).append(
            RiskSnapshotRow(as_of=row.as_of, score=row.score, level=row.level)
        )
    return grouped


def load_snapshots(
    db: Session, student_id: int, as_of: date
) -> list[RiskSnapshotRow]:
    return load_snapshots_bulk(db, [student_id], as_of).get(student_id, [])


def _series_out(result: TrendResult) -> TrendSeriesOut:
    return TrendSeriesOut(
        label=result.label,
        slope=result.slope,
        point_count=result.point_count,
        first=result.first,
        last=result.last,
        mean=result.mean,
        sudden_change=result.sudden_change,
        points=[
            TrendPointOut(on=point.on, value=point.value) for point in result.points
        ],
    )


def get_trends(db: Session, student: Student, as_of: date) -> TrendsOut:
    data = load(db, [student.id], as_of)[0]
    snapshots = load_snapshots(db, student.id, as_of)
    trends = build_student_trends(data, snapshots)
    subjects: dict[int, Subject] = {}
    if data.subject_ids:
        subjects = {
            row.id: row
            for row in db.execute(
                select(Subject).where(Subject.id.in_(data.subject_ids))
            ).scalars().all()
        }
    return TrendsOut(
        student_id=student.id,
        as_of=as_of,
        overall=_series_out(trends.overall),
        by_type=[
            TypedTrendOut(type=assessment_type, **_series_out(result).model_dump())
            for assessment_type, result in trends.by_type.items()
        ],
        by_subject=[
            SubjectTrendOut(
                subject_id=subject_id,
                subject_code=subjects[subject_id].code,
                subject_name=subjects[subject_id].name,
                **_series_out(result).model_dump(),
            )
            for subject_id, result in trends.by_subject.items()
            if subject_id in subjects
        ],
        attendance=_series_out(trends.attendance),
        risk=_series_out(trends.risk),
    )


def get_warnings(db: Session, student: Student, as_of: date) -> WarningsOut:
    data = load(db, [student.id], as_of)[0]
    snapshots = load_snapshots(db, student.id, as_of)
    return WarningsOut(
        student_id=student.id,
        as_of=as_of,
        warnings=[
            WarningOut(
                code=item.code,
                severity=item.severity,
                message=item.message,
                metric=item.metric,
                previous_value=item.previous_value,
                current_value=item.current_value,
            )
            for item in detect_warnings(data, snapshots)
        ],
    )
