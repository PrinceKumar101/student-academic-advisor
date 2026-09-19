from __future__ import annotations

from datetime import UTC, date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.ai.client import AIClient, AIClientError, get_ai_client
from app.ai.fallback import fallback_plan
from app.ai.prompts import plan_v1
from app.ai.prompts.plan_v1 import PlanPromptSlot
from app.ai.schemas import PlanAdvice
from app.ai.validators import validate_plan_output
from app.core.config import Settings, get_settings
from app.core.errors import AppError, Forbidden, NotFound, RateLimited
from app.engines.analytics import analyze_subjects
from app.engines.time_budget import SubjectConcern, TimeSlot, allocate
from app.models.enrollment import Enrollment
from app.models.enums import FallbackReason, Source, SubjectBand, UserRole
from app.models.student import Student
from app.models.study_plan import StudyPlan, StudyPlanItem
from app.models.subject import Subject
from app.models.user import User
from app.schemas.study_plans import (
    StudyPlanCreate,
    StudyPlanItemOut,
    StudyPlanOut,
    StudyPlanSubjectOut,
    StudyPlanSummaryOut,
)
from app.services.academic_data_loader import load

AUTO_PICK_LIMIT = 3
MAX_EXAM_DAYS = 60


def count_plans_today(
    db: Session, user_id: int, *, now: datetime
) -> int:
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)
    start = datetime(now.year, now.month, now.day, tzinfo=UTC)
    rows = db.execute(
        select(func.count())
        .select_from(StudyPlan)
        .where(
            StudyPlan.created_by_user_id == user_id,
            StudyPlan.created_at >= start,
        )
    ).scalar_one()
    return int(rows or 0)


def _require_student(user: User) -> Student:
    if user.role != UserRole.STUDENT or user.student is None:
        raise Forbidden("Only a student can manage study plans")
    return user.student


def _validate_exam_date(exam_date: date, as_of: date) -> None:
    days = (exam_date - as_of).days
    if days < 1 or days > MAX_EXAM_DAYS:
        raise AppError(
            "VALIDATION_ERROR",
            "exam_date must be in the future and within 60 days",
            422,
        )


def _enrolled_subjects(db: Session, student_id: int) -> dict[int, Subject]:
    rows = db.execute(
        select(Subject)
        .join(Enrollment, Enrollment.subject_id == Subject.id)
        .where(Enrollment.student_id == student_id)
    ).scalars().all()
    return {row.id: row for row in rows}


def _auto_pick(analyses, enrolled: dict[int, Subject]) -> list[Subject]:
    by_id = {item.subject_id: item for item in analyses}

    def sort_key(subject: Subject) -> tuple[bool, float, str]:
        item = by_id.get(subject.id)
        percent = item.performance_percent if item is not None else None
        value = percent if percent is not None else 0.0
        return (percent is not None, value, subject.code)

    weak = [
        enrolled[item.subject_id]
        for item in analyses
        if item.subject_id in enrolled
        and (
            item.band is SubjectBand.HIGH_CONCERN
            or (
                item.performance_percent is not None
                and item.performance_percent < 50
            )
        )
    ]
    pool = weak or list(enrolled.values())
    ranked = sorted(pool, key=sort_key)
    return ranked[:AUTO_PICK_LIMIT]


def _resolve_subjects(
    db: Session,
    student: Student,
    body: StudyPlanCreate,
    as_of: date,
) -> list[Subject]:
    enrolled = _enrolled_subjects(db, student.id)
    if not enrolled:
        raise AppError(
            "VALIDATION_ERROR",
            "Student has no enrolled subjects",
            422,
        )
    if body.subject_ids:
        missing = [sid for sid in body.subject_ids if sid not in enrolled]
        if missing:
            raise AppError(
                "VALIDATION_ERROR",
                "subject_ids must belong to the student",
                422,
                {"unknown_ids": missing},
            )
        return [enrolled[sid] for sid in body.subject_ids]

    data = load(db, [student.id], as_of)[0]
    return _auto_pick(analyze_subjects(data), enrolled)


def _concerns(
    db: Session,
    student: Student,
    subjects: list[Subject],
    as_of: date,
) -> list[SubjectConcern]:
    data = load(db, [student.id], as_of)[0]
    analysis = {item.subject_id: item for item in analyze_subjects(data)}
    return [
        SubjectConcern(
            subject_id=subject.id,
            subject_code=subject.code,
            percent=(
                analysis[subject.id].performance_percent
                if subject.id in analysis
                else None
            ),
        )
        for subject in subjects
    ]


def _topics_by_code(
    subjects: list[Subject], topics: dict[int, list[str]]
) -> dict[str, list[str]]:
    by_id = {subject.id: subject.code for subject in subjects}
    result: dict[str, list[str]] = {}
    for subject_id, names in topics.items():
        code = by_id.get(subject_id)
        if code is None:
            continue
        cleaned = [name.strip() for name in names if name.strip()]
        if cleaned:
            result[code] = cleaned
    return result


def _fill_text(
    slots: list[TimeSlot],
    allowed_topics: dict[str, list[str]],
    *,
    client: AIClient,
    settings: Settings,
    user_id: int,
) -> tuple[PlanAdvice, Source, str | None, str | None]:
    expected = [slot.slot_id for slot in slots]
    subject_codes = {slot.slot_id: slot.subject_code for slot in slots}
    try:
        completion = client.complete(
            plan_v1.build_messages(
                [
                    PlanPromptSlot(
                        slot_id=slot.slot_id,
                        date=slot.date.isoformat(),
                        subject_code=slot.subject_code,
                        minutes=slot.minutes,
                        priority=slot.priority.value,
                    )
                    for slot in slots
                ],
                allowed_topics,
            ),
            feature="plan",
            timeout_seconds=settings.ai_plan_timeout_seconds,
            max_tokens=settings.ai_max_tokens_plan,
            user_id=user_id,
        )
    except AIClientError as exc:
        return (
            fallback_plan(expected, subject_codes, allowed_topics),
            Source.FALLBACK,
            exc.reason,
            None,
        )

    outcome = validate_plan_output(
        completion.text, expected, allowed_topics, subject_codes
    )
    if outcome.ok and outcome.advice is not None:
        return outcome.advice, Source.AI, None, completion.model
    return (
        fallback_plan(expected, subject_codes, allowed_topics),
        Source.FALLBACK,
        outcome.reason or "INVALID_OUTPUT",
        None,
    )


def _item_out(item: StudyPlanItem) -> StudyPlanItemOut:
    return StudyPlanItemOut(
        id=item.id,
        plan_date=item.plan_date,
        subject=StudyPlanSubjectOut(id=item.subject.id, code=item.subject.code),
        topic=item.topic,
        activity=item.activity,
        duration_minutes=item.duration_minutes,
        priority=item.priority,
        is_completed=item.is_completed,
        completed_at=item.completed_at,
    )


def _plan_out(plan: StudyPlan) -> StudyPlanOut:
    payload = plan.inputs or {}
    reason = payload.get("fallback_reason")
    return StudyPlanOut(
        id=plan.id,
        exam_date=plan.exam_date,
        available_hours_per_day=plan.available_hours_per_day,
        source=plan.source,
        prompt_version=plan.prompt_version,
        created_at=plan.created_at,
        items=[
            _item_out(item)
            for item in sorted(plan.items, key=lambda row: (row.plan_date, row.id))
        ],
        tips=list(payload.get("tips") or []),
        fallback_reason=FallbackReason(reason) if reason else None,
    )


def _load_owned(db: Session, plan_id: int, student_id: int) -> StudyPlan:
    plan = db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.items).selectinload(StudyPlanItem.subject))
        .where(StudyPlan.id == plan_id)
    ).scalar_one_or_none()
    if plan is None:
        raise NotFound("Study plan not found")
    if plan.student_id != student_id:
        raise Forbidden("Cannot access another student's plan")
    return plan


def create_plan(
    db: Session,
    user: User,
    body: StudyPlanCreate,
    *,
    as_of: date | None = None,
    now: datetime | None = None,
    client: AIClient | None = None,
    settings: Settings | None = None,
) -> StudyPlanOut:
    student = _require_student(user)
    settings = settings or get_settings()
    client = client or get_ai_client()
    as_of = as_of or date.today()
    now = now or datetime.now(UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    _validate_exam_date(body.exam_date, as_of)
    if count_plans_today(db, user.id, now=now) >= settings.ai_daily_plan_limit:
        raise RateLimited("Daily study plan limit reached")

    subjects = _resolve_subjects(db, student, body, as_of)
    concerns = _concerns(db, student, subjects, as_of)
    slots = allocate(
        concerns,
        exam_date=body.exam_date,
        available_hours_per_day=body.available_hours_per_day,
        as_of=as_of,
    )
    allowed = _topics_by_code(subjects, body.topics)
    advice, source, reason, model = _fill_text(
        slots,
        allowed,
        client=client,
        settings=settings,
        user_id=user.id,
    )
    text_by_id = {item.slot_id: item for item in advice.slots}

    plan = StudyPlan(
        student_id=student.id,
        exam_date=body.exam_date,
        available_hours_per_day=body.available_hours_per_day,
        inputs={
            "subject_ids": [subject.id for subject in subjects],
            "topics": {str(key): value for key, value in body.topics.items()},
            "tips": advice.tips,
            "fallback_reason": reason,
        },
        source=source,
        model=model,
        prompt_version=plan_v1.PROMPT_VERSION,
        created_by_user_id=user.id,
        created_at=now,
    )
    db.add(plan)
    db.flush()
    for slot in slots:
        text = text_by_id[slot.slot_id]
        db.add(
            StudyPlanItem(
                plan_id=plan.id,
                plan_date=slot.date,
                subject_id=slot.subject_id,
                topic=text.topic,
                activity=text.activity,
                duration_minutes=slot.minutes,
                priority=slot.priority,
            )
        )
    db.commit()
    return _plan_out(_load_owned(db, plan.id, student.id))


def list_plans(db: Session, user: User) -> list[StudyPlanSummaryOut]:
    student = _require_student(user)
    rows = db.execute(
        select(StudyPlan)
        .options(selectinload(StudyPlan.items))
        .where(StudyPlan.student_id == student.id)
        .order_by(StudyPlan.created_at.desc(), StudyPlan.id.desc())
    ).scalars().all()
    return [
        StudyPlanSummaryOut(
            id=row.id,
            exam_date=row.exam_date,
            available_hours_per_day=row.available_hours_per_day,
            source=row.source,
            created_at=row.created_at,
            item_count=len(row.items),
        )
        for row in rows
    ]


def get_plan(db: Session, user: User, plan_id: int) -> StudyPlanOut:
    student = _require_student(user)
    return _plan_out(_load_owned(db, plan_id, student.id))


def patch_item(
    db: Session,
    user: User,
    plan_id: int,
    item_id: int,
    *,
    is_completed: bool,
    now: datetime | None = None,
) -> StudyPlanItemOut:
    student = _require_student(user)
    plan = _load_owned(db, plan_id, student.id)
    item = next((row for row in plan.items if row.id == item_id), None)
    if item is None:
        raise NotFound("Study plan item not found")
    now = now or datetime.now(UTC)
    item.is_completed = is_completed
    item.completed_at = now if is_completed else None
    db.commit()
    db.refresh(item)
    return _item_out(item)


def delete_plan(db: Session, user: User, plan_id: int) -> None:
    student = _require_student(user)
    plan = _load_owned(db, plan_id, student.id)
    db.delete(plan)
    db.commit()
