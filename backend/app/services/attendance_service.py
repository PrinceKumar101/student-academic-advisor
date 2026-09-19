from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.api.deps import authorize_teacher_subject_write
from app.core.errors import AppError, Conflict, NotFound
from app.models.attendance import AttendanceRecord
from app.models.enrollment import Enrollment
from app.models.student import Student
from app.models.user import User
from app.schemas.attendance import (
    AttendanceListOut,
    AttendanceRecordCreate,
    AttendanceRecordOut,
    AttendanceRecordUpdate,
    AttendanceSummaryOut,
)
from app.services.percent import attendance_percent


def _record_out(record: AttendanceRecord) -> AttendanceRecordOut:
    return AttendanceRecordOut(
        id=record.id,
        student_id=record.enrollment.student_id,
        subject_id=record.enrollment.subject_id,
        record_date=record.record_date,
        classes_held=record.classes_held,
        classes_attended=record.classes_attended,
    )


def _get_enrollment(db: Session, student_id: int, subject_id: int) -> Enrollment:
    enrollment = db.execute(
        select(Enrollment)
        .options(selectinload(Enrollment.subject))
        .where(
            Enrollment.student_id == student_id,
            Enrollment.subject_id == subject_id,
        )
    ).scalar_one_or_none()
    if enrollment is None:
        raise NotFound("Enrollment not found")
    return enrollment


def list_attendance(
    db: Session, student: Student, subject_id: int | None
) -> AttendanceListOut:
    stmt = (
        select(Enrollment)
        .options(
            selectinload(Enrollment.subject),
            selectinload(Enrollment.attendance_records),
        )
        .where(Enrollment.student_id == student.id)
    )
    if subject_id is not None:
        stmt = stmt.where(Enrollment.subject_id == subject_id)
    enrollments = db.execute(stmt.order_by(Enrollment.subject_id)).scalars().all()
    summaries: list[AttendanceSummaryOut] = []
    records: list[AttendanceRecordOut] = []
    for enrollment in enrollments:
        held = sum(row.classes_held for row in enrollment.attendance_records)
        attended = sum(row.classes_attended for row in enrollment.attendance_records)
        summaries.append(
            AttendanceSummaryOut(
                subject_id=enrollment.subject_id,
                subject_code=enrollment.subject.code,
                subject_name=enrollment.subject.name,
                classes_held=held,
                classes_attended=attended,
                attendance_percent=attendance_percent(held, attended),
            )
        )
        for row in sorted(
            enrollment.attendance_records, key=lambda item: item.record_date
        ):
            records.append(_record_out(row))
    return AttendanceListOut(
        student_id=student.id, summaries=summaries, records=records
    )


def create_attendance(
    db: Session, current_user: User, body: AttendanceRecordCreate
) -> AttendanceRecordOut:
    student = db.get(Student, body.student_id)
    if student is None:
        raise NotFound("Student not found")
    authorize_teacher_subject_write(db, current_user, body.subject_id, student)
    enrollment = _get_enrollment(db, body.student_id, body.subject_id)
    record = AttendanceRecord(
        enrollment_id=enrollment.id,
        record_date=body.record_date,
        classes_held=body.classes_held,
        classes_attended=body.classes_attended,
    )
    db.add(record)
    try:
        db.commit()
        db.refresh(record)
        record = db.execute(
            select(AttendanceRecord)
            .options(selectinload(AttendanceRecord.enrollment))
            .where(AttendanceRecord.id == record.id)
        ).scalar_one()
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Attendance record already exists for this date") from exc
    return _record_out(record)


def _loaded_record(db: Session, record_id: int) -> AttendanceRecord:
    record = db.execute(
        select(AttendanceRecord)
        .options(
            selectinload(AttendanceRecord.enrollment).selectinload(Enrollment.student)
        )
        .where(AttendanceRecord.id == record_id)
    ).scalar_one_or_none()
    if record is None:
        raise NotFound("Attendance record not found")
    return record


def update_attendance(
    db: Session, current_user: User, record_id: int, body: AttendanceRecordUpdate
) -> AttendanceRecordOut:
    record = _loaded_record(db, record_id)
    student = record.enrollment.student
    authorize_teacher_subject_write(
        db, current_user, record.enrollment.subject_id, student
    )
    data = body.model_dump(exclude_unset=True)
    held = data.get("classes_held", record.classes_held)
    attended = data.get("classes_attended", record.classes_attended)
    if attended > held:
        raise AppError(
            "VALIDATION_ERROR",
            "classes_attended cannot exceed classes_held",
            422,
        )
    for key, value in data.items():
        setattr(record, key, value)
    try:
        db.commit()
        db.refresh(record)
    except IntegrityError as exc:
        db.rollback()
        raise Conflict("Attendance record already exists for this date") from exc
    return _record_out(record)


def delete_attendance(db: Session, current_user: User, record_id: int) -> None:
    record = _loaded_record(db, record_id)
    authorize_teacher_subject_write(
        db, current_user, record.enrollment.subject_id, record.enrollment.student
    )
    db.delete(record)
    db.commit()
