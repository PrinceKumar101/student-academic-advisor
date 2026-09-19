from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    AttendanceRecord,
    Enrollment,
    RiskAssessment,
    RiskLevel,
    SemesterResult,
    Student,
    StudyHabit,
    Subject,
    Teacher,
    TeachingAssignment,
    User,
    UserRole,
)
from scripts.seed_generator import (
    DEFAULT_AS_OF,
    DEMO_PASSWORD,
    MISSINGASSIGN_EMAIL,
    NEWSTUDENT_EMAIL,
    PROFILE_DECLINING,
    PROFILE_HIGH,
    PROFILE_LOW,
    RAHUL_EMAIL,
    ZEROCLASS_EMAIL,
    seed_demo,
    snapshot_as_of_dates,
)


def _snapshot(session: Session) -> dict[str, object]:
    students = session.scalars(select(Student).order_by(Student.student_code)).all()
    subjects = {
        subject.id: subject.code for subject in session.scalars(select(Subject))
    }
    enrollments = session.scalars(select(Enrollment).order_by(Enrollment.id)).all()
    enrollment_key = {
        enrollment.id: (
            next(
                student.student_code
                for student in students
                if student.id == enrollment.student_id
            ),
            subjects[enrollment.subject_id],
        )
        for enrollment in enrollments
    }
    attendance = [
        (
            *enrollment_key[row.enrollment_id],
            row.record_date.isoformat(),
            row.classes_held,
            row.classes_attended,
        )
        for row in session.scalars(
            select(AttendanceRecord).order_by(
                AttendanceRecord.enrollment_id, AttendanceRecord.record_date
            )
        )
    ]
    assessments = [
        (
            *enrollment_key[row.enrollment_id],
            row.type.value,
            row.name,
            row.max_marks,
            row.obtained_marks,
            row.status.value,
            row.assessment_date.isoformat(),
        )
        for row in session.scalars(
            select(Assessment).order_by(Assessment.enrollment_id, Assessment.name)
        )
    ]
    results = [
        (student.student_code, row.semester, row.percentage, row.sgpa)
        for student in students
        for row in session.scalars(
            select(SemesterResult)
            .where(SemesterResult.student_id == student.id)
            .order_by(SemesterResult.semester)
        )
    ]
    habits = [
        (
            student.student_code,
            row.study_hours_per_day,
            row.self_confidence,
            row.available_hours_per_day,
        )
        for student in students
        if (row := session.scalar(
            select(StudyHabit).where(StudyHabit.student_id == student.id)
        ))
        is not None
    ]
    teachers = [
        (user.email, teacher.full_name, teacher.department)
        for teacher, user in session.execute(
            select(Teacher, User)
            .join(User, Teacher.user_id == User.id)
            .order_by(User.email)
        )
    ]
    assignments = [
        (user.email, subject.code, assignment.section)
        for assignment, teacher, user, subject in session.execute(
            select(TeachingAssignment, Teacher, User, Subject)
            .join(Teacher, TeachingAssignment.teacher_id == Teacher.id)
            .join(User, Teacher.user_id == User.id)
            .join(Subject, TeachingAssignment.subject_id == Subject.id)
            .order_by(User.email, Subject.code, TeachingAssignment.section)
        )
    ]
    risks = [
        (
            row.student_id,
            row.as_of.isoformat(),
            row.score,
            row.level.value,
            row.data_completeness,
            row.config_version,
        )
        for row in session.scalars(
            select(RiskAssessment).order_by(
                RiskAssessment.student_id, RiskAssessment.as_of
            )
        )
    ]
    return {
        "risks": risks,
        "student_emails": [
            session.get(User, student.user_id).email for student in students
        ],
        "codes": [student.student_code for student in students],
        "sections": [(student.student_code, student.section) for student in students],
        "attendance": attendance,
        "assessments": assessments,
        "results": results,
        "habits": habits,
        "teachers": teachers,
        "assignments": assignments,
    }


def test_seed_counts_match_schema(db_session: Session) -> None:
    result = seed_demo(db_session, as_of=DEFAULT_AS_OF)
    db_session.commit()

    assert db_session.scalar(select(func.count()).select_from(Student)) == 43
    assert db_session.scalar(select(func.count()).select_from(Teacher)) == 2
    assert db_session.scalar(select(func.count()).select_from(Subject)) == 5
    assert (
        db_session.scalar(
            select(func.count()).select_from(User).where(User.role == UserRole.STUDENT)
        )
        == 43
    )
    assert db_session.scalar(select(func.count()).select_from(Enrollment)) == 210
    assert db_session.scalar(select(func.count()).select_from(AttendanceRecord)) == 2520
    assert db_session.scalar(select(func.count()).select_from(Assessment)) == 2050
    assert db_session.scalar(select(func.count()).select_from(SemesterResult)) == 82
    assert db_session.scalar(select(func.count()).select_from(StudyHabit)) == 41
    assert db_session.scalar(select(func.count()).select_from(TeachingAssignment)) == 6
    assert db_session.scalar(select(func.count()).select_from(RiskAssessment)) == 43 * 4

    generated_profiles = [
        profile
        for email, profile in result.profiles_by_email.items()
        if not profile.startswith("EDGE_")
    ]
    assert generated_profiles.count("HIGH") == 6
    assert generated_profiles.count("AVERAGE") == 12
    assert generated_profiles.count("LOW") == 7
    assert generated_profiles.count("IMPROVING") == 5
    assert generated_profiles.count("DECLINING") == 6
    assert generated_profiles.count("INCONSISTENT") == 4
    assert result.profiles_by_email[RAHUL_EMAIL] == PROFILE_DECLINING


def test_seed_is_deterministic(db_session: Session, db_engine) -> None:
    seed_demo(db_session, as_of=date(2026, 9, 19))
    db_session.commit()
    first = _snapshot(db_session)

    from sqlalchemy.orm import sessionmaker

    from app.db.init import create_all, drop_all

    drop_all(db_engine)
    create_all(db_engine)
    other = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)()
    try:
        seed_demo(other, as_of=date(2026, 9, 19))
        other.commit()
        second = _snapshot(other)
    finally:
        other.close()

    assert first == second


def test_story_and_edge_students(db_session: Session) -> None:
    seed_demo(db_session)
    db_session.commit()

    rahul_user = db_session.scalar(select(User).where(User.email == RAHUL_EMAIL))
    assert rahul_user is not None
    assert verify_password(DEMO_PASSWORD, rahul_user.password_hash)

    rahul = db_session.scalar(select(Student).where(Student.user_id == rahul_user.id))
    assert rahul is not None
    assert rahul.section == "B"
    assert rahul.semester == 5

    new_user = db_session.scalar(select(User).where(User.email == NEWSTUDENT_EMAIL))
    new_student = db_session.scalar(
        select(Student).where(Student.user_id == new_user.id)
    )
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(Enrollment)
            .where(Enrollment.student_id == new_student.id)
        )
        == 0
    )

    zero_user = db_session.scalar(select(User).where(User.email == ZEROCLASS_EMAIL))
    zero = db_session.scalar(select(Student).where(Student.user_id == zero_user.id))
    held_sum, attended_sum = db_session.execute(
        select(
            func.coalesce(func.sum(AttendanceRecord.classes_held), 0),
            func.coalesce(func.sum(AttendanceRecord.classes_attended), 0),
        )
        .join(Enrollment, AttendanceRecord.enrollment_id == Enrollment.id)
        .where(Enrollment.student_id == zero.id)
    ).one()
    assert held_sum == 0
    assert attended_sum == 0
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(Assessment)
            .join(Enrollment, Assessment.enrollment_id == Enrollment.id)
            .where(Enrollment.student_id == zero.id)
        )
        == 0
    )

    missing_user = db_session.scalar(
        select(User).where(User.email == MISSINGASSIGN_EMAIL)
    )
    missing = db_session.scalar(
        select(Student).where(Student.user_id == missing_user.id)
    )
    missing_count = db_session.scalar(
        select(func.count())
        .select_from(Assessment)
        .join(Enrollment, Assessment.enrollment_id == Enrollment.id)
        .where(
            Enrollment.student_id == missing.id,
            Assessment.type == AssessmentType.ASSIGNMENT,
            Assessment.status == AssessmentStatus.MISSING,
        )
    )
    assert missing_count >= 10

    snapshots = db_session.scalars(
        select(RiskAssessment).where(RiskAssessment.student_id == rahul.id)
    ).all()
    assert {row.as_of for row in snapshots} == set(snapshot_as_of_dates(DEFAULT_AS_OF))
    current = max(snapshots, key=lambda row: row.as_of)
    assert current.level is RiskLevel.HIGH

    teacher1 = db_session.scalar(select(User).where(User.email == "teacher1@demo.edu"))
    teacher2 = db_session.scalar(select(User).where(User.email == "teacher2@demo.edu"))
    assert verify_password(DEMO_PASSWORD, teacher1.password_hash)
    assert verify_password(DEMO_PASSWORD, teacher2.password_hash)


def test_seed_profile_risk_bands(db_session: Session) -> None:
    result = seed_demo(db_session)
    db_session.commit()
    current_as_of = snapshot_as_of_dates(result.as_of)[-1]

    email_by_student = {
        student.id: db_session.get(User, student.user_id).email
        for student in db_session.scalars(select(Student))
    }
    current = {
        email_by_student[row.student_id]: row
        for row in db_session.scalars(
            select(RiskAssessment).where(RiskAssessment.as_of == current_as_of)
        )
    }

    assert current[RAHUL_EMAIL].level is RiskLevel.HIGH
    assert current[NEWSTUDENT_EMAIL].level is RiskLevel.INSUFFICIENT_DATA

    for email, profile in result.profiles_by_email.items():
        level = current[email].level
        if profile == PROFILE_HIGH:
            assert level is RiskLevel.LOW, email
        if profile == PROFILE_LOW:
            assert level is RiskLevel.HIGH, email


def test_generated_students_have_full_subject_history(db_session: Session) -> None:
    seed_demo(db_session)
    db_session.commit()

    rahul_id = db_session.scalar(
        select(Student.id)
        .join(User, Student.user_id == User.id)
        .where(User.email == RAHUL_EMAIL)
    )
    edge_ids = set(
        db_session.scalars(
            select(Student.id)
            .join(User, Student.user_id == User.id)
            .where(
                User.email.in_(
                    (NEWSTUDENT_EMAIL, ZEROCLASS_EMAIL, MISSINGASSIGN_EMAIL)
                )
            )
        )
    )
    generated = db_session.scalars(
        select(Student).where(Student.id.not_in(edge_ids))
    ).all()
    assert len(generated) == 40
    assert rahul_id in {student.id for student in generated}

    for student in generated:
        enrollments = db_session.scalars(
            select(Enrollment).where(Enrollment.student_id == student.id)
        ).all()
        assert len(enrollments) == 5
        for enrollment in enrollments:
            weeks = db_session.scalar(
                select(func.count())
                .select_from(AttendanceRecord)
                .where(AttendanceRecord.enrollment_id == enrollment.id)
            )
            assessments = db_session.scalar(
                select(func.count())
                .select_from(Assessment)
                .where(Assessment.enrollment_id == enrollment.id)
            )
            assert weeks == 12
            assert assessments == 10
        assert (
            db_session.scalar(
                select(func.count())
                .select_from(SemesterResult)
                .where(SemesterResult.student_id == student.id)
            )
            == 2
        )
        assert (
            db_session.scalar(
                select(StudyHabit).where(StudyHabit.student_id == student.id)
            )
            is not None
        )
