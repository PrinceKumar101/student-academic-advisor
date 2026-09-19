from datetime import date

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import (
    list_visible_students,
    teacher_can_write_subject,
    visible_students_stmt,
)
from app.api.pagination import page_offset, to_page
from app.core.errors import Forbidden, NotFound
from app.engines.analytics import class_analytics
from app.engines.risk_config import round1
from app.models.enrollment import Enrollment
from app.models.enums import RiskLevel, TrendLabel, UserRole
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.common import Page, PageParams
from app.schemas.teacher import (
    SubjectAnalyticsOut,
    SubjectMeanOut,
    TeacherDashboardOut,
    TeacherStudentOut,
)
from app.services.analytics_service import build_student_analytics_rows


def _require_teacher(user: User) -> int:
    if user.role != UserRole.TEACHER or user.teacher is None:
        raise Forbidden("Only a teacher can access teacher APIs")
    return user.teacher.id


def _subject_means(
    db: Session, subject_means: dict[int, float]
) -> list[SubjectMeanOut]:
    if not subject_means:
        return []
    subjects = {
        row.id: row
        for row in db.execute(
            select(Subject).where(Subject.id.in_(subject_means.keys()))
        ).scalars().all()
    }
    return [
        SubjectMeanOut(
            subject_id=subject_id,
            code=subjects[subject_id].code,
            name=subjects[subject_id].name,
            mean_percent=mean,
        )
        for subject_id, mean in sorted(subject_means.items())
        if subject_id in subjects
    ]


def _dashboard_from_rows(
    db: Session, rows, as_of: date
) -> TeacherDashboardOut:
    summary = class_analytics(rows)
    return TeacherDashboardOut(
        as_of=as_of,
        group_size=summary.group_size,
        risk_counts=summary.risk_counts,
        mean_attendance=summary.mean_attendance,
        mean_marks=summary.mean_marks,
        subject_performance=_subject_means(db, summary.subject_means),
        trend_distribution=summary.trend_distribution,
    )


def get_dashboard(
    db: Session, user: User, *, as_of: date | None = None
) -> TeacherDashboardOut:
    teacher_id = _require_teacher(user)
    as_of = as_of or date.today()
    students = list_visible_students(db, teacher_id)
    rows = build_student_analytics_rows(db, students, as_of)
    return _dashboard_from_rows(db, rows, as_of)


def _filter_students(
    db: Session,
    teacher_id: int,
    *,
    department: str | None,
    semester: int | None,
    section: str | None,
    subject_id: int | None,
    search: str | None,
) -> list[Student]:
    stmt = visible_students_stmt(teacher_id)
    if department:
        stmt = stmt.where(Student.department == department)
    if semester is not None:
        stmt = stmt.where(Student.semester == semester)
    if section:
        stmt = stmt.where(Student.section == section)
    if subject_id is not None:
        stmt = stmt.where(Enrollment.subject_id == subject_id)
    if search:
        term = f"%{search.strip()}%"
        stmt = stmt.where(
            or_(
                Student.full_name.ilike(term),
                Student.student_code.ilike(term),
            )
        )
    stmt = stmt.order_by(Student.full_name.asc(), Student.id.asc())
    return list(db.execute(stmt).scalars().unique().all())


def list_students(
    db: Session,
    user: User,
    params: PageParams,
    *,
    risk_level: RiskLevel | None = None,
    department: str | None = None,
    semester: int | None = None,
    section: str | None = None,
    subject_id: int | None = None,
    search: str | None = None,
    as_of: date | None = None,
) -> Page[TeacherStudentOut]:
    teacher_id = _require_teacher(user)
    as_of = as_of or date.today()
    if subject_id is not None and not teacher_can_write_subject(
        db, teacher_id, subject_id
    ):
        raise Forbidden("Not assigned to this subject")

    students = _filter_students(
        db,
        teacher_id,
        department=department,
        semester=semester,
        section=section,
        subject_id=subject_id,
        search=search,
    )
    rows = build_student_analytics_rows(db, students, as_of)
    by_id = {row.student_id: row for row in rows}
    items: list[TeacherStudentOut] = []
    for student in students:
        analytics = by_id[student.id]
        if risk_level is not None and analytics.risk_level != risk_level.value:
            continue
        items.append(
            TeacherStudentOut(
                id=student.id,
                student_code=student.student_code,
                full_name=student.full_name,
                department=student.department,
                semester=student.semester,
                section=student.section,
                risk_score=analytics.risk_score,
                risk_level=(
                    RiskLevel(analytics.risk_level)
                    if analytics.risk_level
                    else None
                ),
                attendance_percent=(
                    None
                    if analytics.attendance_percent is None
                    else round1(analytics.attendance_percent)
                ),
                marks_percent=(
                    None
                    if analytics.marks_percent is None
                    else round1(analytics.marks_percent)
                ),
                trend_label=(
                    TrendLabel(analytics.trend_label)
                    if analytics.trend_label
                    else None
                ),
            )
        )

    total = len(items)
    start = page_offset(params)
    page_items = items[start : start + params.page_size]
    return to_page(page_items, total, params)


def get_subject_analytics(
    db: Session,
    user: User,
    subject_id: int,
    *,
    as_of: date | None = None,
) -> SubjectAnalyticsOut:
    teacher_id = _require_teacher(user)
    as_of = as_of or date.today()
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise NotFound("Subject not found")
    if not teacher_can_write_subject(db, teacher_id, subject_id):
        raise Forbidden("Not assigned to this subject")

    students = _filter_students(
        db,
        teacher_id,
        department=None,
        semester=None,
        section=None,
        subject_id=subject_id,
        search=None,
    )
    rows = build_student_analytics_rows(db, students, as_of)
    summary = _dashboard_from_rows(db, rows, as_of)
    return SubjectAnalyticsOut(
        subject_id=subject.id,
        code=subject.code,
        name=subject.name,
        **summary.model_dump(),
    )
