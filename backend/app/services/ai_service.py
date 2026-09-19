from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.ai.client import AIClient, AIClientError, get_ai_client
from app.ai.context_builder import (
    FactorFact,
    StudentAcademicContext,
    SubjectMeta,
    TrendFact,
    WarningFact,
    build_context,
)
from app.ai.fallback import fallback_analysis, fallback_chat, fallback_suggestions
from app.ai.prompts import analysis_v1, chat_v1, suggest_v1
from app.ai.schemas import AnalysisAdvice, ChatAdvice, InterventionSuggestionsAdvice
from app.ai.validators import (
    validate_analysis_output,
    validate_chat_output,
    validate_suggestions_output,
)
from app.core.config import Settings, get_settings
from app.core.errors import Forbidden, RateLimited
from app.engines.analytics import analyze_subjects, overall_attendance_percent
from app.engines.risk_config import COMPONENT_KEYS
from app.engines.trend_engine import build_student_trends
from app.engines.warnings import detect_warnings
from app.models.ai_advice import AIAdvice
from app.models.ai_chat_message import AIChatMessage
from app.models.enums import (
    AdviceKind,
    ChatMessageRole,
    FallbackReason,
    Source,
    UserRole,
)
from app.models.student import Student
from app.models.subject import Subject
from app.models.user import User
from app.schemas.ai import (
    AnalysisAdviceOut,
    AnalysisOut,
    ChatHistoryOut,
    ChatMessageOut,
    ChatOut,
    InterventionSuggestionOut,
    InterventionSuggestionsOut,
    UsageBucketOut,
    UsageOut,
)
from app.services.academic_data_loader import load
from app.services.risk_service import compute_for_student
from app.services.study_plan_service import count_plans_today
from app.services.trend_service import load_snapshots

HISTORY_WINDOW = 6


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def _utc_day_start(now: datetime) -> datetime:
    now = _aware(now)
    return datetime(now.year, now.month, now.day, tzinfo=UTC)


def _bucket(used: int, limit: int) -> UsageBucketOut:
    remaining = max(0, limit - used)
    return UsageBucketOut(used=used, limit=limit, remaining=remaining)


def _count_analysis_today(
    db: Session, user_id: int, *, now: datetime, settings: Settings
) -> int:
    del settings
    start = _utc_day_start(now)
    rows = db.execute(
        select(func.count())
        .select_from(AIAdvice)
        .where(
            AIAdvice.created_by_user_id == user_id,
            AIAdvice.kind == AdviceKind.ANALYSIS,
            AIAdvice.created_at >= start,
        )
    ).scalar_one()
    return int(rows or 0)


def usage_for_user(
    db: Session,
    user: User,
    *,
    now: datetime | None = None,
    settings: Settings | None = None,
) -> UsageOut:
    settings = settings or get_settings()
    now = now or datetime.now(UTC)
    used = _count_analysis_today(db, user.id, now=now, settings=settings)
    plans_used = count_plans_today(db, user.id, now=now)
    chat_used = 0
    if user.student is not None:
        chat_used = _count_chat_today(db, user.student.id, now=now)
    return UsageOut(
        analysis=_bucket(used, settings.ai_daily_analysis_limit),
        chat=_bucket(chat_used, settings.ai_daily_chat_limit),
        plans=_bucket(plans_used, settings.ai_daily_plan_limit),
    )


def _count_chat_today(db: Session, student_id: int, *, now: datetime) -> int:
    start = _utc_day_start(now)
    rows = db.execute(
        select(func.count())
        .select_from(AIChatMessage)
        .where(
            AIChatMessage.student_id == student_id,
            AIChatMessage.role == ChatMessageRole.USER,
            AIChatMessage.created_at >= start,
        )
    ).scalar_one()
    return int(rows or 0)


def _require_student(user: User) -> Student:
    if user.role != UserRole.STUDENT or user.student is None:
        raise Forbidden("Only a student can use academic chat")
    return user.student


def _recent_messages(db: Session, student_id: int) -> list[AIChatMessage]:
    rows = (
        db.execute(
            select(AIChatMessage)
            .where(AIChatMessage.student_id == student_id)
            .order_by(AIChatMessage.created_at.desc(), AIChatMessage.id.desc())
            .limit(HISTORY_WINDOW)
        )
        .scalars()
        .all()
    )
    return list(reversed(rows))


def _store_chat_turn(
    db: Session,
    *,
    student_id: int,
    question: str,
    advice: ChatAdvice,
    source: Source,
    created_at: datetime,
) -> None:
    db.add(
        AIChatMessage(
            student_id=student_id,
            role=ChatMessageRole.USER,
            content=question,
            source=None,
            created_at=created_at,
        )
    )
    db.add(
        AIChatMessage(
            student_id=student_id,
            role=ChatMessageRole.ASSISTANT,
            content=advice.answer,
            source=source,
            created_at=created_at,
        )
    )
    db.commit()


def list_chat_history(db: Session, user: User) -> ChatHistoryOut:
    student = _require_student(user)
    rows = (
        db.execute(
            select(AIChatMessage)
            .where(AIChatMessage.student_id == student.id)
            .order_by(AIChatMessage.created_at.asc(), AIChatMessage.id.asc())
        )
        .scalars()
        .all()
    )
    return ChatHistoryOut(
        messages=[
            ChatMessageOut(
                id=row.id,
                role=row.role,
                content=row.content,
                source=row.source,
                created_at=row.created_at,
            )
            for row in rows
        ]
    )


def clear_chat_history(db: Session, user: User) -> None:
    student = _require_student(user)
    db.execute(
        delete(AIChatMessage).where(AIChatMessage.student_id == student.id)
    )
    db.commit()


def answer_academic_question(
    db: Session,
    user: User,
    question: str,
    *,
    as_of: date | None = None,
    now: datetime | None = None,
    client: AIClient | None = None,
    settings: Settings | None = None,
) -> ChatOut:
    settings = settings or get_settings()
    client = client or get_ai_client()
    as_of = as_of or date.today()
    now = now or datetime.now(UTC)
    student = _require_student(user)

    if _count_chat_today(db, student.id, now=now) >= settings.ai_daily_chat_limit:
        raise RateLimited("Daily AI chat limit reached")

    context = _assemble_context(db, student, as_of)
    history = [
        {"role": row.role.value, "content": row.content}
        for row in _recent_messages(db, student.id)
    ]

    source = Source.FALLBACK
    reason: str | None = None
    advice: ChatAdvice
    try:
        completion = client.complete(
            chat_v1.build_messages(context, question, history),
            feature="chat",
            timeout_seconds=settings.ai_timeout_seconds,
            max_tokens=settings.ai_max_tokens_chat,
            user_id=user.id,
        )
        outcome = validate_chat_output(completion.text, context)
        if outcome.ok and outcome.advice is not None:
            advice = outcome.advice
            source = Source.AI
        else:
            reason = outcome.reason or "INVALID_OUTPUT"
            advice = fallback_chat(question, context)
    except AIClientError as exc:
        reason = exc.reason
        advice = fallback_chat(question, context)

    _store_chat_turn(
        db,
        student_id=student.id,
        question=question,
        advice=advice,
        source=source,
        created_at=now,
    )
    return ChatOut(
        source=source,
        generated_at=now,
        answer=advice.answer,
        suggested_followups=advice.suggested_followups,
        fallback_reason=FallbackReason(reason) if reason else None,
    )


def _lookup_cache(
    db: Session,
    student_id: int,
    input_hash: str,
    *,
    now: datetime,
    settings: Settings,
) -> AIAdvice | None:
    cutoff = now - timedelta(hours=settings.ai_cache_ttl_hours)
    return db.execute(
        select(AIAdvice)
        .where(
            AIAdvice.student_id == student_id,
            AIAdvice.kind == AdviceKind.ANALYSIS,
            AIAdvice.input_hash == input_hash,
            AIAdvice.created_at >= cutoff,
        )
        .order_by(AIAdvice.created_at.desc(), AIAdvice.id.desc())
        .limit(1)
    ).scalar_one_or_none()


def _row_to_out(row: AIAdvice, *, cached: bool) -> AnalysisOut:
    payload = row.payload
    reason = payload.get("fallback_reason")
    return AnalysisOut(
        source=row.source,
        generated_at=row.created_at,
        cached=cached,
        facts=payload.get("facts") or {},
        advice=AnalysisAdviceOut.model_validate(payload["advice"]),
        fallback_reason=FallbackReason(reason) if reason else None,
    )


def _assemble_context(
    db: Session, student: Student, as_of: date
) -> StudentAcademicContext:
    data = load(db, [student.id], as_of)[0]
    risk_out = compute_for_student(db, student, as_of)
    snapshots = load_snapshots(db, student.id, as_of)
    trends = build_student_trends(data, snapshots)
    warnings = detect_warnings(data, snapshots)
    analyses = analyze_subjects(data)
    subjects: dict[int, Subject] = {}
    if data.subject_ids:
        subjects = {
            row.id: row
            for row in db.execute(
                select(Subject).where(Subject.id.in_(data.subject_ids))
            ).scalars().all()
        }

    component_map = {item.key: item for item in risk_out.components}
    top_factors = []
    for key in risk_out.top_factors:
        component = component_map.get(key)
        top_factors.append(
            FactorFact(
                key=key,
                raw_value=component.raw_value if component else None,
                unit=component.unit if component else None,
                risk=component.risk if component else None,
            )
        )

    subject_rows = []
    for item in analyses:
        meta = subjects.get(item.subject_id)
        if meta is None:
            continue
        subject_rows.append(
            (
                SubjectMeta(code=meta.code, name=meta.name),
                item.attendance_percent,
                item.performance_percent,
                item.band.value if item.band else None,
            )
        )

    trend_facts = [
        TrendFact(
            series="overall",
            label=trends.overall.label.value,
            first=trends.overall.first,
            last=trends.overall.last,
        ),
        TrendFact(
            series="attendance",
            label=trends.attendance.label.value
            if trends.attendance is not None
            else "INSUFFICIENT_DATA",
            first=trends.attendance.first if trends.attendance else None,
            last=trends.attendance.last if trends.attendance else None,
        ),
    ]

    return build_context(
        overall_attendance_percent=overall_attendance_percent(data.attendance),
        subject_rows=subject_rows,
        risk_score=risk_out.score,
        risk_level=risk_out.level.value,
        data_completeness=risk_out.data_completeness,
        top_factors=top_factors,
        trends=trend_facts,
        warnings=[
            WarningFact(
                code=item.code,
                severity=item.severity.value,
                message=item.message,
                metric=item.metric,
                previous_value=item.previous_value,
                current_value=item.current_value,
            )
            for item in warnings
        ],
        study_hours_per_day=(
            data.study_habit.study_hours_per_day if data.study_habit else None
        ),
        self_confidence=(
            data.study_habit.self_confidence if data.study_habit else None
        ),
        extra_factor_keys=list(COMPONENT_KEYS),
    )


def _store(
    db: Session,
    *,
    student_id: int,
    user_id: int,
    context: StudentAcademicContext,
    advice: AnalysisAdvice,
    source: Source,
    fallback_reason: str | None,
    model: str | None,
    created_at: datetime,
) -> AIAdvice:
    row = AIAdvice(
        student_id=student_id,
        kind=AdviceKind.ANALYSIS,
        input_hash=context.input_hash(),
        payload={
            "facts": context.to_facts_dict(),
            "advice": advice.model_dump(),
            "fallback_reason": fallback_reason,
        },
        source=source,
        model=model,
        prompt_version=analysis_v1.PROMPT_VERSION,
        created_by_user_id=user_id,
        created_at=created_at,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def analyze_performance(
    db: Session,
    student: Student,
    user: User,
    *,
    refresh: bool = False,
    as_of: date | None = None,
    now: datetime | None = None,
    client: AIClient | None = None,
    settings: Settings | None = None,
) -> AnalysisOut:
    settings = settings or get_settings()
    client = client or get_ai_client()
    as_of = as_of or date.today()
    now = now or datetime.now(UTC)

    context = _assemble_context(db, student, as_of)
    digest = context.input_hash()
    if not refresh:
        cached = _lookup_cache(db, student.id, digest, now=now, settings=settings)
        if cached is not None:
            return _row_to_out(cached, cached=True)

    used = _count_analysis_today(db, user.id, now=now, settings=settings)
    if used >= settings.ai_daily_analysis_limit:
        raise RateLimited("Daily AI analysis limit reached")

    source = Source.FALLBACK
    reason: str | None = None
    model: str | None = None
    advice: AnalysisAdvice
    try:
        completion = client.complete(
            analysis_v1.build_messages(context),
            feature="analysis",
            timeout_seconds=settings.ai_timeout_seconds,
            max_tokens=settings.ai_max_tokens_analysis,
            user_id=user.id,
        )
        outcome = validate_analysis_output(completion.text, context)
        if outcome.ok and outcome.advice is not None:
            advice = outcome.advice
            source = Source.AI
            model = completion.model
        else:
            reason = outcome.reason or "INVALID_OUTPUT"
            advice = fallback_analysis(context)
    except AIClientError as exc:
        reason = exc.reason
        advice = fallback_analysis(context)

    row = _store(
        db,
        student_id=student.id,
        user_id=user.id,
        context=context,
        advice=advice,
        source=source,
        fallback_reason=reason,
        model=model,
        created_at=now,
    )
    return _row_to_out(row, cached=False)


def suggest_interventions(
    db: Session,
    student: Student,
    user: User,
    *,
    as_of: date | None = None,
    now: datetime | None = None,
    client: AIClient | None = None,
    settings: Settings | None = None,
) -> InterventionSuggestionsOut:
    settings = settings or get_settings()
    client = client or get_ai_client()
    as_of = as_of or date.today()
    now = now or datetime.now(UTC)
    if user.role != UserRole.TEACHER:
        raise Forbidden("Only a teacher can request intervention suggestions")

    context = _assemble_context(db, student, as_of)
    source = Source.FALLBACK
    reason: str | None = None
    advice: InterventionSuggestionsAdvice
    try:
        completion = client.complete(
            suggest_v1.build_messages(context),
            feature="intervention_suggestions",
            timeout_seconds=settings.ai_timeout_seconds,
            max_tokens=settings.ai_max_tokens_analysis,
            user_id=user.id,
        )
        outcome = validate_suggestions_output(completion.text, context)
        if outcome.ok and outcome.advice is not None:
            advice = outcome.advice
            source = Source.AI
        else:
            reason = outcome.reason or "INVALID_OUTPUT"
            advice = fallback_suggestions(context)
    except AIClientError as exc:
        reason = exc.reason
        advice = fallback_suggestions(context)

    return InterventionSuggestionsOut(
        source=source,
        generated_at=now,
        student_id=student.id,
        prompt_version=suggest_v1.PROMPT_VERSION,
        suggestions=[
            InterventionSuggestionOut.model_validate(item.model_dump())
            for item in advice.suggestions
        ],
        fallback_reason=FallbackReason(reason) if reason else None,
    )
