from __future__ import annotations

import csv
import io
from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import teacher_can_write_subject
from app.core.errors import AppError, Forbidden
from app.models.assessment import Assessment
from app.models.attendance import AttendanceRecord
from app.models.enrollment import Enrollment
from app.models.enums import AssessmentStatus, AssessmentType, UserRole
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.imports import ImportResultOut, ImportRowError

ATTENDANCE_COLUMNS = (
    "student_code",
    "subject_code",
    "record_date",
    "classes_held",
    "classes_attended",
)
ASSESSMENT_COLUMNS = (
    "student_code",
    "subject_code",
    "type",
    "name",
    "max_marks",
    "obtained_marks",
    "status",
    "assessment_date",
)


def _require_teacher(user: User) -> int:
    if user.role != UserRole.TEACHER or user.teacher is None:
        raise Forbidden("Only a teacher can import academic records")
    return user.teacher.id


def _parse_csv(content: bytes, required: tuple[str, ...]) -> list[dict[str, str]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AppError("VALIDATION_ERROR", "CSV must be UTF-8 encoded", 422) from exc
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise AppError("VALIDATION_ERROR", "CSV is missing a header row", 422)
    headers = [name.strip() for name in reader.fieldnames if name]
    missing = [col for col in required if col not in headers]
    if missing:
        raise AppError(
            "VALIDATION_ERROR",
            f"CSV is missing columns: {', '.join(missing)}",
            422,
        )
    rows: list[dict[str, str]] = []
    for raw in reader:
        rows.append(
            {
                key.strip(): (value or "").strip()
                for key, value in raw.items()
                if key
            }
        )
    return rows


def _error(row: int, code: str, message: str) -> ImportRowError:
    return ImportRowError(row=row, code=code, message=message)


def _lookup_student(db: Session, code: str) -> Student | None:
    return db.execute(
        select(Student).where(Student.student_code == code)
    ).scalar_one_or_none()


def _lookup_subject(db: Session, code: str) -> Subject | None:
    return db.execute(select(Subject).where(Subject.code == code)).scalar_one_or_none()


def _lookup_enrollment(
    db: Session, student_id: int, subject_id: int
) -> Enrollment | None:
    return db.execute(
        select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.subject_id == subject_id,
        )
    ).scalar_one_or_none()


def _parse_int(value: str, field: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an integer") from exc


def _parse_float(value: str, field: str) -> float:
    try:
        return float(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be a number") from exc


def _parse_date(value: str, field: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date") from exc


def import_attendance(
    db: Session, user: User, content: bytes, *, dry_run: bool
) -> ImportResultOut:
    teacher_id = _require_teacher(user)
    parsed_rows = _parse_csv(content, ATTENDANCE_COLUMNS)
    errors: list[ImportRowError] = []
    pending: list[dict[str, Any]] = []
    seen: set[tuple[int, date]] = set()

    for index, raw in enumerate(parsed_rows, start=2):
        student_code = raw.get("student_code", "")
        subject_code = raw.get("subject_code", "")
        if not student_code or not subject_code:
            errors.append(
                _error(
                    index,
                    "VALIDATION_ERROR",
                    "student and subject codes required",
                )
            )
            continue
        student = _lookup_student(db, student_code)
        subject = _lookup_subject(db, subject_code)
        if student is None:
            errors.append(
                _error(index, "NOT_FOUND", f"Unknown student_code {student_code}")
            )
            continue
        if subject is None:
            errors.append(
                _error(index, "NOT_FOUND", f"Unknown subject_code {subject_code}")
            )
            continue
        if not teacher_can_write_subject(db, teacher_id, subject.id, student):
            errors.append(
                _error(index, "FORBIDDEN", "Not assigned to this subject or section")
            )
            continue
        enrollment = _lookup_enrollment(db, student.id, subject.id)
        if enrollment is None:
            errors.append(
                _error(index, "NOT_FOUND", "Student is not enrolled in this subject")
            )
            continue
        try:
            record_date = _parse_date(raw.get("record_date", ""), "record_date")
            held = _parse_int(raw.get("classes_held", ""), "classes_held")
            attended = _parse_int(raw.get("classes_attended", ""), "classes_attended")
        except ValueError as exc:
            errors.append(_error(index, "VALIDATION_ERROR", str(exc)))
            continue
        if held < 0 or attended < 0 or attended > held:
            errors.append(
                _error(
                    index,
                    "VALIDATION_ERROR",
                    "classes_held >= 0 and attended within held",
                )
            )
            continue
        key = (enrollment.id, record_date)
        if key in seen:
            errors.append(_error(index, "CONFLICT", "Duplicate date in this file"))
            continue
        seen.add(key)
        existing = db.execute(
            select(AttendanceRecord).where(
                AttendanceRecord.enrollment_id == enrollment.id,
                AttendanceRecord.record_date == record_date,
            )
        ).scalar_one_or_none()
        if existing is not None:
            errors.append(
                _error(index, "CONFLICT", "Attendance already exists for this date")
            )
            continue
        pending.append(
            {
                "enrollment_id": enrollment.id,
                "record_date": record_date,
                "classes_held": held,
                "classes_attended": attended,
            }
        )

    return _finish(
        db,
        kind="attendance",
        dry_run=dry_run,
        errors=errors,
        pending=pending,
        build=lambda item: AttendanceRecord(**item),
    )


def import_assessments(
    db: Session, user: User, content: bytes, *, dry_run: bool
) -> ImportResultOut:
    teacher_id = _require_teacher(user)
    parsed_rows = _parse_csv(content, ASSESSMENT_COLUMNS)
    errors: list[ImportRowError] = []
    pending: list[dict[str, Any]] = []

    for index, raw in enumerate(parsed_rows, start=2):
        student_code = raw.get("student_code", "")
        subject_code = raw.get("subject_code", "")
        if not student_code or not subject_code:
            errors.append(
                _error(
                    index,
                    "VALIDATION_ERROR",
                    "student and subject codes required",
                )
            )
            continue
        student = _lookup_student(db, student_code)
        subject = _lookup_subject(db, subject_code)
        if student is None:
            errors.append(
                _error(index, "NOT_FOUND", f"Unknown student_code {student_code}")
            )
            continue
        if subject is None:
            errors.append(
                _error(index, "NOT_FOUND", f"Unknown subject_code {subject_code}")
            )
            continue
        if not teacher_can_write_subject(db, teacher_id, subject.id, student):
            errors.append(
                _error(index, "FORBIDDEN", "Not assigned to this subject or section")
            )
            continue
        enrollment = _lookup_enrollment(db, student.id, subject.id)
        if enrollment is None:
            errors.append(
                _error(index, "NOT_FOUND", "Student is not enrolled in this subject")
            )
            continue
        try:
            assessment_type = AssessmentType(raw.get("type", ""))
            status = AssessmentStatus(raw.get("status", ""))
            name = raw.get("name", "")
            max_marks = _parse_float(raw.get("max_marks", ""), "max_marks")
            obtained_raw = raw.get("obtained_marks", "")
            obtained = None
            if obtained_raw != "":
                obtained = _parse_float(obtained_raw, "obtained_marks")
            assessment_date = _parse_date(
                raw.get("assessment_date", ""), "assessment_date"
            )
        except ValueError as exc:
            errors.append(_error(index, "VALIDATION_ERROR", str(exc)))
            continue
        if not name:
            errors.append(_error(index, "VALIDATION_ERROR", "name is required"))
            continue
        if max_marks <= 0:
            errors.append(_error(index, "VALIDATION_ERROR", "max_marks must be > 0"))
            continue
        if obtained is not None and (obtained < 0 or obtained > max_marks):
            errors.append(
                _error(index, "VALIDATION_ERROR", "obtained_marks out of range")
            )
            continue
        if status == AssessmentStatus.GRADED and obtained is None:
            errors.append(
                _error(index, "VALIDATION_ERROR", "GRADED requires obtained_marks")
            )
            continue
        pending.append(
            {
                "enrollment_id": enrollment.id,
                "type": assessment_type,
                "name": name,
                "max_marks": max_marks,
                "obtained_marks": obtained,
                "status": status,
                "assessment_date": assessment_date,
            }
        )

    return _finish(
        db,
        kind="assessments",
        dry_run=dry_run,
        errors=errors,
        pending=pending,
        build=lambda item: Assessment(**item),
    )


def _finish(
    db: Session,
    *,
    kind: str,
    dry_run: bool,
    errors: list[ImportRowError],
    pending: list[dict[str, Any]],
    build,
) -> ImportResultOut:
    valid = not errors
    if not valid or dry_run:
        return ImportResultOut(
            kind=kind,
            dry_run=dry_run,
            valid=valid,
            committed=False,
            created_count=len(pending) if valid else 0,
            errors=errors,
        )
    for item in pending:
        db.add(build(item))
    db.commit()
    return ImportResultOut(
        kind=kind,
        dry_run=False,
        valid=True,
        committed=True,
        created_count=len(pending),
        errors=[],
    )
