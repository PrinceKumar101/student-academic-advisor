from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.assessment import Assessment
from app.models.attendance import AttendanceRecord
from app.models.enrollment import Enrollment
from app.models.enums import AssessmentStatus, AssessmentType, UserRole
from app.models.semester_result import SemesterResult
from app.models.student import Student
from app.models.study_habit import StudyHabit
from app.models.subject import Subject
from app.models.teacher import Teacher
from app.models.teaching_assignment import TeachingAssignment
from app.models.user import User


def add_student(
    db: Session,
    *,
    password_hash: str,
    email: str,
    student_code: str,
    full_name: str = "Student",
    department: str = "CS",
    semester: int = 5,
    section: str = "A",
    is_active: bool = True,
) -> tuple[User, Student]:
    user = User(
        email=email,
        password_hash=password_hash,
        role=UserRole.STUDENT,
        is_active=is_active,
    )
    db.add(user)
    db.flush()
    student = Student(
        user_id=user.id,
        student_code=student_code,
        full_name=full_name,
        department=department,
        semester=semester,
        section=section,
    )
    db.add(student)
    db.commit()
    db.refresh(user)
    db.refresh(student)
    return user, student


def add_teacher(
    db: Session,
    *,
    password_hash: str,
    email: str,
    full_name: str = "Teacher",
    department: str = "CS",
) -> tuple[User, Teacher]:
    user = User(
        email=email,
        password_hash=password_hash,
        role=UserRole.TEACHER,
    )
    db.add(user)
    db.flush()
    teacher = Teacher(
        user_id=user.id,
        full_name=full_name,
        department=department,
    )
    db.add(teacher)
    db.commit()
    db.refresh(user)
    db.refresh(teacher)
    return user, teacher


def add_subject(db: Session, *, code: str, name: str, semester: int = 5) -> Subject:
    subject = Subject(code=code, name=name, semester=semester)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def enroll(db: Session, student: Student, subject: Subject) -> Enrollment:
    enrollment = Enrollment(student_id=student.id, subject_id=subject.id)
    db.add(enrollment)
    db.commit()
    return enrollment


def assign_teacher(
    db: Session,
    teacher: Teacher,
    subject: Subject,
    section: str = "ALL",
) -> TeachingAssignment:
    assignment = TeachingAssignment(
        teacher_id=teacher.id,
        subject_id=subject.id,
        section=section,
    )
    db.add(assignment)
    db.commit()
    return assignment


def add_attendance(
    db: Session,
    enrollment: Enrollment,
    *,
    record_date: date,
    classes_held: int,
    classes_attended: int,
) -> AttendanceRecord:
    record = AttendanceRecord(
        enrollment_id=enrollment.id,
        record_date=record_date,
        classes_held=classes_held,
        classes_attended=classes_attended,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def add_assessment(
    db: Session,
    enrollment: Enrollment,
    *,
    assessment_date: date,
    name: str = "Quiz 1",
    assessment_type: AssessmentType = AssessmentType.QUIZ,
    max_marks: float = 10,
    obtained_marks: float | None = 8,
    status: AssessmentStatus = AssessmentStatus.GRADED,
) -> Assessment:
    row = Assessment(
        enrollment_id=enrollment.id,
        type=assessment_type,
        name=name,
        max_marks=max_marks,
        obtained_marks=obtained_marks,
        status=status,
        assessment_date=assessment_date,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def add_semester_result(
    db: Session,
    student: Student,
    *,
    semester: int,
    percentage: float,
    sgpa: float | None = None,
) -> SemesterResult:
    row = SemesterResult(
        student_id=student.id,
        semester=semester,
        percentage=percentage,
        sgpa=sgpa,
    )
    db.add(row)
    db.commit()
    return row


def add_study_habit(
    db: Session,
    student: Student,
    *,
    study_hours_per_day: float = 2.0,
    self_confidence: int = 3,
    available_hours_per_day: float = 3.0,
) -> StudyHabit:
    row = StudyHabit(
        student_id=student.id,
        study_hours_per_day=study_hours_per_day,
        self_confidence=self_confidence,
        available_hours_per_day=available_hours_per_day,
    )
    db.add(row)
    db.commit()
    return row


def bearer(
    client: TestClient, email: str, password: str = "Demo@1234"
) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
