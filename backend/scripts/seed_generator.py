"""Deterministic synthetic seed used by `scripts.seed_demo` and tests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from random import Random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import (
    Assessment,
    AssessmentStatus,
    AssessmentType,
    AttendanceRecord,
    Enrollment,
    RiskAssessment,
    SemesterResult,
    Student,
    StudyHabit,
    Subject,
    Teacher,
    TeachingAssignment,
    User,
    UserRole,
)

RNG_SEED = 42
DEFAULT_AS_OF = date(2026, 9, 19)
DEMO_PASSWORD = "Demo@1234"
DEPARTMENT = "CSE"
CURRENT_SEMESTER = 5
WEEKS = 12
CLASSES_PER_WEEK = 5

PROFILE_HIGH = "HIGH"
PROFILE_AVERAGE = "AVERAGE"
PROFILE_LOW = "LOW"
PROFILE_IMPROVING = "IMPROVING"
PROFILE_DECLINING = "DECLINING"
PROFILE_INCONSISTENT = "INCONSISTENT"

SUBJECTS: tuple[tuple[str, str], ...] = (
    ("CS301", "Data Structures"),
    ("CS302", "DBMS"),
    ("CS303", "Operating Systems"),
    ("CS304", "Computer Networks"),
    ("CS305", "Software Engineering"),
)

TEACHER_SPECS: tuple[tuple[str, str, tuple[tuple[str, str], ...]], ...] = (
    (
        "teacher1@demo.edu",
        "Kiran Vale",
        (("CS301", "ALL"), ("CS302", "ALL"), ("CS303", "ALL")),
    ),
    (
        "teacher2@demo.edu",
        "Mira Cobalt",
        (("CS304", "ALL"), ("CS305", "ALL"), ("CS301", "B")),
    ),
)

# 39 fictional names for generated students other than the story login.
GENERATED_NAMES: tuple[str, ...] = (
    "Asha Thornfield",
    "Benji Calder",
    "Cora Lindell",
    "Dev Patelton",
    "Elia Marwood",
    "Farah Quill",
    "Gita Northam",
    "Hari Solace",
    "Isha Fenwick",
    "Jovan Bramble",
    "Kavya Oakley",
    "Liam Crest",
    "Meera Dunlap",
    "Nia Holloway",
    "Omar Brightwell",
    "Priya Sandoval",
    "Quinn Adler",
    "Ravi Pendleton",
    "Sana Whitlock",
    "Tara Glenford",
    "Uday Kessler",
    "Vera Langston",
    "Willa Crompton",
    "Xavier Holt",
    "Yara Newcomb",
    "Zane Whitaker",
    "Anika Rowlett",
    "Bharat Keene",
    "Celia Drummond",
    "Deepa Harlow",
    "Evan Shore",
    "Fiona Greaves",
    "Gopal Merritt",
    "Hana Voss",
    "Irfan Colby",
    "Jaya Redmond",
    "Kian Barlow",
    "Lila Prescott",
    "Mohan Ellison",
)

RAHUL_EMAIL = "rahul@demo.edu"
RAHUL_NAME = "Rahul Venn"
NEWSTUDENT_EMAIL = "newstudent@demo.edu"
ZEROCLASS_EMAIL = "zeroclass@demo.edu"
MISSINGASSIGN_EMAIL = "missingassign@demo.edu"

ASSESSMENT_PLAN: tuple[tuple[AssessmentType, str, float, int], ...] = (
    (AssessmentType.INTERNAL, "Internal 1", 30.0, 3),
    (AssessmentType.INTERNAL, "Internal 2", 30.0, 7),
    (AssessmentType.INTERNAL, "Internal 3", 30.0, 11),
    (AssessmentType.QUIZ, "Quiz 1", 10.0, 1),
    (AssessmentType.QUIZ, "Quiz 2", 10.0, 4),
    (AssessmentType.QUIZ, "Quiz 3", 10.0, 8),
    (AssessmentType.QUIZ, "Quiz 4", 10.0, 10),
    (AssessmentType.ASSIGNMENT, "Assignment 1", 20.0, 2),
    (AssessmentType.ASSIGNMENT, "Assignment 2", 20.0, 6),
    (AssessmentType.ASSIGNMENT, "Assignment 3", 20.0, 9),
)


@dataclass(frozen=True)
class SeedResult:
    as_of: date
    profiles_by_email: dict[str, str]


def week_dates(as_of: date, weeks: int = WEEKS) -> list[date]:
    return [as_of - timedelta(weeks=(weeks - 1 - index)) for index in range(weeks)]


def _clip(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _lerp(start: float, end: float, t: float) -> float:
    return start + (end - start) * t


def _email_from_name(full_name: str) -> str:
    return full_name.lower().replace(" ", ".") + "@demo.edu"


def _created_at(as_of: date) -> datetime:
    return datetime(as_of.year, as_of.month, as_of.day, tzinfo=UTC)


def _remaining_profiles(rng: Random) -> list[str]:
    slots = (
        [PROFILE_HIGH] * 6
        + [PROFILE_AVERAGE] * 12
        + [PROFILE_LOW] * 7
        + [PROFILE_IMPROVING] * 5
        + [PROFILE_DECLINING] * 5
        + [PROFILE_INCONSISTENT] * 4
    )
    rng.shuffle(slots)
    return slots


def _mark_percent(
    profile: str,
    index: int,
    total: int,
    rng: Random,
    *,
    story: bool,
    week_index: int = 0,
) -> float:
    if story:
        # Decline by calendar week so later internals are weak (rahul ends HIGH).
        week_t = week_index / (WEEKS - 1)
        return _clip(_lerp(46.0, 26.0, week_t) + rng.uniform(-1.0, 1.0), 0.0, 100.0)
    if profile == PROFILE_HIGH:
        return rng.uniform(82.0, 95.0)
    if profile == PROFILE_AVERAGE:
        return rng.uniform(60.0, 72.0)
    if profile == PROFILE_LOW:
        return rng.uniform(35.0, 50.0)
    if profile == PROFILE_IMPROVING:
        week_t = week_index / (WEEKS - 1)
        return _clip(_lerp(42.0, 88.0, week_t) + rng.uniform(-1.0, 1.0), 0.0, 100.0)
    if profile == PROFILE_DECLINING:
        week_t = week_index / (WEEKS - 1)
        return _clip(_lerp(85.0, 40.0, week_t) + rng.uniform(-1.0, 1.0), 0.0, 100.0)
    return _clip(rng.gauss(60.0, 15.0), 20.0, 95.0)


def _attendance_rate(
    profile: str, week_index: int, rng: Random, *, story: bool
) -> float:
    t = week_index / (WEEKS - 1)
    if story:
        return _lerp(72.0, 44.0, t)
    if profile == PROFILE_HIGH:
        return rng.uniform(90.0, 98.0)
    if profile == PROFILE_AVERAGE:
        return rng.uniform(78.0, 88.0)
    if profile == PROFILE_LOW:
        return rng.uniform(60.0, 72.0)
    if profile == PROFILE_IMPROVING:
        return _lerp(55.0, 92.0, t)
    if profile == PROFILE_DECLINING:
        return _lerp(90.0, 55.0, t)
    return _clip(rng.gauss(75.0, 10.0), 50.0, 95.0)


def _submit_assignment(
    profile: str, assignment_index: int, rng: Random, *, story: bool
) -> bool:
    t = assignment_index / 2
    if story:
        return rng.random() < _lerp(0.70, 0.35, t)
    rates = {
        PROFILE_HIGH: 0.98,
        PROFILE_AVERAGE: 0.90,
        PROFILE_LOW: 0.60,
        PROFILE_INCONSISTENT: rng.uniform(0.4, 0.9),
        PROFILE_IMPROVING: _lerp(0.55, 0.92, t),
        PROFILE_DECLINING: _lerp(0.95, 0.50, t),
    }
    return rng.random() < rates[profile]


def _study_habit_values(
    profile: str, rng: Random, *, story: bool
) -> tuple[float, int, float]:
    if story:
        return 0.8, 1, 2.5
    ranges = {
        PROFILE_HIGH: ((3.0, 5.0), (4, 5)),
        PROFILE_AVERAGE: ((2.0, 3.0), (3, 3)),
        PROFILE_LOW: ((0.5, 1.5), (1, 2)),
        PROFILE_IMPROVING: ((2.2, 3.5), (3, 4)),
        PROFILE_DECLINING: ((0.8, 2.0), (2, 3)),
        PROFILE_INCONSISTENT: ((1.0, 4.0), (2, 4)),
    }
    hours_range, conf_range = ranges[profile]
    hours = round(rng.uniform(*hours_range), 1)
    confidence = rng.randint(conf_range[0], conf_range[1])
    available = round(_clip(hours + rng.uniform(1.0, 3.0), hours, 24.0), 1)
    return hours, confidence, available


def _semester_percentages(
    profile: str, rng: Random, *, story: bool
) -> tuple[float, float]:
    if story:
        return 72.0, 55.0
    if profile == PROFILE_IMPROVING:
        return round(rng.uniform(48.0, 56.0), 1), round(rng.uniform(58.0, 66.0), 1)
    if profile == PROFILE_DECLINING:
        return round(rng.uniform(74.0, 82.0), 1), round(rng.uniform(62.0, 70.0), 1)
    mid = {
        PROFILE_HIGH: (82.0, 92.0),
        PROFILE_AVERAGE: (62.0, 72.0),
        PROFILE_LOW: (40.0, 52.0),
        PROFILE_INCONSISTENT: (50.0, 70.0),
    }[profile]
    first = round(rng.uniform(*mid), 1)
    second = round(_clip(first + rng.uniform(-3.0, 3.0), 0.0, 100.0), 1)
    return first, second


def _add_user(
    session: Session,
    *,
    email: str,
    role: UserRole,
    password_hash: str,
    created_at: datetime,
) -> User:
    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True,
        created_at=created_at,
    )
    session.add(user)
    session.flush()
    return user


def _add_student(
    session: Session,
    user: User,
    *,
    code: str,
    full_name: str,
    section: str,
    created_at: datetime,
) -> Student:
    student = Student(
        user_id=user.id,
        student_code=code,
        full_name=full_name,
        department=DEPARTMENT,
        semester=CURRENT_SEMESTER,
        section=section,
        created_at=created_at,
    )
    session.add(student)
    session.flush()
    return student


def _enroll_all(
    session: Session, student: Student, subjects: list[Subject]
) -> list[Enrollment]:
    enrollments: list[Enrollment] = []
    for subject in subjects:
        enrollment = Enrollment(student_id=student.id, subject_id=subject.id)
        session.add(enrollment)
        enrollments.append(enrollment)
    session.flush()
    return enrollments


def _add_attendance(
    session: Session,
    enrollments: list[Enrollment],
    dates: list[date],
    profile: str,
    rng: Random,
    *,
    story: bool,
    zero_classes: bool = False,
) -> None:
    for enrollment in enrollments:
        for week_index, record_date in enumerate(dates):
            if zero_classes:
                held, attended = 0, 0
            else:
                rate = _attendance_rate(profile, week_index, rng, story=story)
                held = CLASSES_PER_WEEK
                attended = int(round(held * rate / 100.0))
                attended = max(0, min(held, attended))
            session.add(
                AttendanceRecord(
                    enrollment_id=enrollment.id,
                    record_date=record_date,
                    classes_held=held,
                    classes_attended=attended,
                )
            )


def _add_assessments(
    session: Session,
    enrollments: list[Enrollment],
    dates: list[date],
    profile: str,
    rng: Random,
    *,
    story: bool,
    force_missing_assignments: bool = False,
) -> None:
    total = len(ASSESSMENT_PLAN)
    assignment_index = 0
    for item_index, (kind, name, max_marks, week_index) in enumerate(ASSESSMENT_PLAN):
        assessment_date = dates[week_index]
        percent = _mark_percent(
            profile,
            item_index,
            total,
            rng,
            story=story,
            week_index=week_index,
        )
        for enrollment in enrollments:
            missing = False
            if kind == AssessmentType.ASSIGNMENT:
                if force_missing_assignments:
                    missing = assignment_index < 2 or rng.random() < 0.7
                else:
                    missing = not _submit_assignment(
                        profile, assignment_index, rng, story=story
                    )
            obtained = None if missing else round(max_marks * percent / 100.0, 2)
            obtained = (
                None
                if obtained is None
                else _clip(obtained, 0.0, max_marks)
            )
            session.add(
                Assessment(
                    enrollment_id=enrollment.id,
                    type=kind,
                    name=name,
                    max_marks=max_marks,
                    obtained_marks=obtained,
                    status=(
                        AssessmentStatus.MISSING if missing else AssessmentStatus.GRADED
                    ),
                    assessment_date=assessment_date,
                    created_at=_created_at(assessment_date),
                )
            )
        if kind == AssessmentType.ASSIGNMENT:
            assignment_index += 1


def _add_results_and_habits(
    session: Session,
    student: Student,
    profile: str,
    rng: Random,
    *,
    story: bool,
    created_at: datetime,
) -> None:
    sem3, sem4 = _semester_percentages(profile, rng, story=story)
    session.add(
        SemesterResult(
            student_id=student.id,
            semester=3,
            percentage=sem3,
            sgpa=round(sem3 / 10.0, 2),
        )
    )
    session.add(
        SemesterResult(
            student_id=student.id,
            semester=4,
            percentage=sem4,
            sgpa=round(sem4 / 10.0, 2),
        )
    )
    hours, confidence, available = _study_habit_values(profile, rng, story=story)
    session.add(
        StudyHabit(
            student_id=student.id,
            study_hours_per_day=hours,
            self_confidence=confidence,
            available_hours_per_day=available,
            updated_at=created_at,
        )
    )


SNAPSHOT_WEEK_OFFSETS = (9, 6, 3, 0)


def snapshot_as_of_dates(as_of: date) -> list[date]:
    return [as_of - timedelta(weeks=offset) for offset in SNAPSHOT_WEEK_OFFSETS]


def _backfill_risk_snapshots(
    session: Session, student_ids: list[int], as_of: date
) -> None:
    from app.engines.metrics import to_risk_inputs
    from app.engines.risk_engine import compute_risk
    from app.services.academic_data_loader import load

    for snap_as_of in snapshot_as_of_dates(as_of):
        computed_at = datetime(
            snap_as_of.year, snap_as_of.month, snap_as_of.day, tzinfo=UTC
        )
        for data in load(session, student_ids, snap_as_of):
            result = compute_risk(to_risk_inputs(data), as_of=snap_as_of)
            session.add(
                RiskAssessment(
                    student_id=data.student_id,
                    computed_at=computed_at,
                    as_of=snap_as_of,
                    score=result.score,
                    level=result.level,
                    escalated=result.escalated,
                    escalation_reason=result.escalation_reason,
                    data_completeness=result.data_completeness,
                    config_version=result.config_version,
                    components=result.components_payload(),
                    flags=list(result.flags),
                )
            )
    session.flush()


def seed_demo(
    session: Session,
    as_of: date = DEFAULT_AS_OF,
    *,
    rng_seed: int = RNG_SEED,
) -> SeedResult:
    """Insert the demo dataset. Caller commits. Back-fills 4 risk snapshots."""
    if len(GENERATED_NAMES) != 39:
        raise RuntimeError("GENERATED_NAMES must contain 39 fictional names")

    rng = Random(rng_seed)
    created_at = _created_at(as_of)
    password_hash = hash_password(DEMO_PASSWORD)
    dates = week_dates(as_of)
    profiles_by_email: dict[str, str] = {}

    subjects_by_code: dict[str, Subject] = {}
    for code, name in SUBJECTS:
        subject = Subject(code=code, name=name, semester=CURRENT_SEMESTER)
        session.add(subject)
        subjects_by_code[code] = subject
    session.flush()
    subjects = [subjects_by_code[code] for code, _name in SUBJECTS]

    for email, full_name, assignments in TEACHER_SPECS:
        user = _add_user(
            session,
            email=email,
            role=UserRole.TEACHER,
            password_hash=password_hash,
            created_at=created_at,
        )
        teacher = Teacher(
            user_id=user.id, full_name=full_name, department=DEPARTMENT
        )
        session.add(teacher)
        session.flush()
        for subject_code, section in assignments:
            session.add(
                TeachingAssignment(
                    teacher_id=teacher.id,
                    subject_id=subjects_by_code[subject_code].id,
                    section=section,
                )
            )

    next_code = 1

    def make_student(email: str, full_name: str, section: str) -> Student:
        nonlocal next_code
        user = _add_user(
            session,
            email=email,
            role=UserRole.STUDENT,
            password_hash=password_hash,
            created_at=created_at,
        )
        student = _add_student(
            session,
            user,
            code=f"CS2025{next_code:03d}",
            full_name=full_name,
            section=section,
            created_at=created_at,
        )
        next_code += 1
        return student

    rahul = make_student(RAHUL_EMAIL, RAHUL_NAME, "B")
    profiles_by_email[RAHUL_EMAIL] = PROFILE_DECLINING
    rahul_enrollments = _enroll_all(session, rahul, subjects)
    _add_attendance(
        session, rahul_enrollments, dates, PROFILE_DECLINING, rng, story=True
    )
    _add_assessments(
        session, rahul_enrollments, dates, PROFILE_DECLINING, rng, story=True
    )
    _add_results_and_habits(
        session, rahul, PROFILE_DECLINING, rng, story=True, created_at=created_at
    )

    remaining = zip(GENERATED_NAMES, _remaining_profiles(rng), strict=True)
    for full_name, profile in remaining:
        section = "A" if next_code % 2 == 0 else "B"
        email = _email_from_name(full_name)
        student = make_student(email, full_name, section)
        profiles_by_email[email] = profile
        enrollments = _enroll_all(session, student, subjects)
        _add_attendance(session, enrollments, dates, profile, rng, story=False)
        _add_assessments(session, enrollments, dates, profile, rng, story=False)
        _add_results_and_habits(
            session, student, profile, rng, story=False, created_at=created_at
        )

    make_student(NEWSTUDENT_EMAIL, "Nova Blank", "A")
    profiles_by_email[NEWSTUDENT_EMAIL] = "EDGE_NEW"

    zero = make_student(ZEROCLASS_EMAIL, "Zero Held", "A")
    profiles_by_email[ZEROCLASS_EMAIL] = "EDGE_ZERO"
    zero_enrollments = _enroll_all(session, zero, subjects)
    _add_attendance(
        session,
        zero_enrollments,
        dates,
        PROFILE_AVERAGE,
        rng,
        story=False,
        zero_classes=True,
    )

    missing = make_student(MISSINGASSIGN_EMAIL, "Miss Ingassign", "B")
    profiles_by_email[MISSINGASSIGN_EMAIL] = "EDGE_MISSING"
    missing_enrollments = _enroll_all(session, missing, subjects)
    _add_attendance(
        session, missing_enrollments, dates, PROFILE_AVERAGE, rng, story=False
    )
    _add_assessments(
        session,
        missing_enrollments,
        dates,
        PROFILE_AVERAGE,
        rng,
        story=False,
        force_missing_assignments=True,
    )
    _add_results_and_habits(
        session,
        missing,
        PROFILE_AVERAGE,
        rng,
        story=False,
        created_at=created_at,
    )

    session.flush()
    student_ids = [
        row.id for row in session.scalars(select(Student).order_by(Student.id)).all()
    ]
    _backfill_risk_snapshots(session, student_ids, as_of)
    return SeedResult(as_of=as_of, profiles_by_email=profiles_by_email)
