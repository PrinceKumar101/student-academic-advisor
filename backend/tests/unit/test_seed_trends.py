from sqlalchemy import select
from sqlalchemy.orm import Session

from app.engines.trend_engine import build_student_trends
from app.engines.warnings import detect_warnings
from app.models.enums import TrendLabel
from app.models.student import Student
from app.models.user import User
from app.services.academic_data_loader import load
from app.services.trend_service import load_snapshots
from scripts.seed_generator import (
    DEFAULT_AS_OF,
    PROFILE_IMPROVING,
    RAHUL_EMAIL,
    seed_demo,
)


def test_seeded_rahul_and_improving_trends(db_session: Session) -> None:
    result = seed_demo(db_session, as_of=DEFAULT_AS_OF)
    db_session.commit()

    rahul_user = db_session.scalar(select(User).where(User.email == RAHUL_EMAIL))
    assert rahul_user is not None
    rahul = db_session.scalar(select(Student).where(Student.user_id == rahul_user.id))
    assert rahul is not None
    rahul_data = load(db_session, [rahul.id], DEFAULT_AS_OF)[0]
    rahul_snaps = load_snapshots(db_session, rahul.id, DEFAULT_AS_OF)
    rahul_trends = build_student_trends(rahul_data, rahul_snaps)
    assert rahul_trends.attendance.label is TrendLabel.DECLINING
    assert detect_warnings(rahul_data, rahul_snaps)

    improving_email = next(
        email
        for email, profile in result.profiles_by_email.items()
        if profile == PROFILE_IMPROVING
    )
    improving_user = db_session.scalar(
        select(User).where(User.email == improving_email)
    )
    assert improving_user is not None
    improving = db_session.scalar(
        select(Student).where(Student.user_id == improving_user.id)
    )
    assert improving is not None
    improving_data = load(db_session, [improving.id], DEFAULT_AS_OF)[0]
    improving_snaps = load_snapshots(db_session, improving.id, DEFAULT_AS_OF)
    improving_trends = build_student_trends(improving_data, improving_snaps)
    assert improving_trends.attendance.label is TrendLabel.IMPROVING
