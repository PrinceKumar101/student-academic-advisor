from __future__ import annotations

import re

from app.ai.context_builder import StudentAcademicContext
from app.ai.schemas import (
    AnalysisAdvice,
    ChatAdvice,
    InterventionSuggestion,
    InterventionSuggestionsAdvice,
    MainConcern,
    PlanAdvice,
    PlanSlotText,
    Recommendation,
)

FALLBACK_BANNER = (
    "AI service unavailable. Your academic risk calculation is still available."
)

CHAT_UNAVAILABLE = (
    "The AI assistant is unavailable. Your risk analysis is still available."
)

_ACADEMIC_TERMS = (
    "risk",
    "attend",
    "mark",
    "score",
    "subject",
    "quiz",
    "assignment",
    "study",
    "warning",
    "trend",
    "exam",
    "grade",
    "performance",
    "internal",
    "habit",
    "weak",
    "advisor",
    "recommend",
)

_DEFAULT_FOLLOWUPS = [
    "Why is my risk at this level?",
    "How is my attendance looking?",
    "Which subjects need the most attention?",
]

_FACTOR_LABELS = {
    "attendance": "attendance",
    "internal": "internal marks",
    "assignments": "assignment work",
    "quizzes": "quiz performance",
    "previous": "previous-semester results",
    "study_habits": "study habits",
}


def _priority_for_level(level: str) -> str:
    if level == "HIGH":
        return "HIGH"
    if level == "LOW":
        return "LOW"
    return "MEDIUM"


def _fmt(value: float | None, suffix: str = "") -> str:
    if value is None:
        return "not available"
    text = f"{value:g}"
    return f"{text}{suffix}"


def fallback_analysis(context: StudentAcademicContext) -> AnalysisAdvice:
    priority = _priority_for_level(context.risk_level)
    score = _fmt(context.risk_score)
    attendance = _fmt(context.overall_attendance_percent, "%")
    summary = (
        f"{FALLBACK_BANNER} Risk level is {context.risk_level} "
        f"(risk score of {score}). Overall attendance is {attendance}."
    )
    if len(summary) > 600:
        summary = summary[:600]

    concerns: list[MainConcern] = []
    for factor in context.top_factors[:5]:
        label = _FACTOR_LABELS.get(factor.key, factor.key)
        raw = _fmt(factor.raw_value, "%" if factor.unit == "%" else "")
        concerns.append(
            MainConcern(
                factor=factor.key,
                explanation=(
                    f"The leading risk factor is {label} "
                    f"(recorded value {raw}). Focus improvement here first."
                )[:300],
            )
        )
    for warning in context.warnings:
        if len(concerns) >= 5:
            break
        if warning.metric in context.factor_keys:
            concerns.append(
                MainConcern(
                    factor=warning.metric,
                    explanation=warning.message[:300],
                )
            )
    if not concerns:
        fallback_factor = (
            context.factor_keys[0] if context.factor_keys else "attendance"
        )
        concerns.append(
            MainConcern(
                factor=fallback_factor,
                explanation=(
                    "There is not enough academic history yet to isolate a "
                    "dominant risk factor. Keep recording attendance and marks."
                ),
            )
        )

    weak = context.weak_subjects[0] if context.weak_subjects else None
    recs = [
        Recommendation(
            action="Review the computed risk components and notes on the risk page.",
            reason=(
                "Python already ranked the factors; use those facts to plan study time."
            ),
            priority=priority,
        ),
        Recommendation(
            action="Raise weekly class attendance, especially in weaker subjects.",
            reason=(
                f"Overall attendance is {attendance}."
                + (
                    f" {weak.code} is a weak subject."
                    if weak is not None
                    else ""
                )
            )[:300],
            priority="HIGH" if context.risk_level == "HIGH" else "MEDIUM",
        ),
        Recommendation(
            action="Complete overdue assignments and revise recent quiz topics.",
            reason=(
                "Missing work and declining quiz scores are common drivers "
                "of elevated risk."
            ),
            priority="MEDIUM",
        ),
    ]
    if context.study_hours_per_day is not None and context.study_hours_per_day < 2:
        recs.append(
            Recommendation(
                action="Increase daily study time in small, scheduled blocks.",
                reason=(
                    "Recorded study time is "
                    f"{context.study_hours_per_day:g} hours per day."
                ),
                priority="MEDIUM",
            )
        )
    if weak is not None:
        recs.append(
            Recommendation(
                action=f"Prioritize revision for {weak.name} ({weak.code}).",
                reason=(
                    "This subject is flagged as weak from the calculated "
                    "performance or concern band."
                ),
                priority="HIGH",
            )
        )
    return AnalysisAdvice(
        summary=summary,
        main_concerns=concerns[:5],
        recommendations=recs[:6],
        priority=priority,
    )


def fallback_plan(
    slot_ids: list[str],
    subject_codes: dict[str, str],
    allowed_topics: dict[str, list[str]],
) -> PlanAdvice:
    slots: list[PlanSlotText] = []
    for slot_id in slot_ids:
        code = subject_codes[slot_id]
        topics = allowed_topics.get(code) or []
        topic = topics[0] if topics else f"Suggested: {code} revision"
        slots.append(
            PlanSlotText(
                slot_id=slot_id,
                topic=topic[:80],
                activity=(
                    f"Revise notes and solve 5 practice questions for {code}"
                )[:200],
            )
        )
    return PlanAdvice(
        slots=slots,
        tips=[
            "Keep each block to the scheduled minutes.",
            "Finish weaker subjects first when energy is highest.",
            "Tick items off as you complete them.",
        ],
    )


def _normalize_question(question: str) -> str:
    return re.sub(r"[^a-z0-9\s]+", " ", question.lower()).strip()


def _is_academic_question(normalized: str) -> bool:
    return any(term in normalized for term in _ACADEMIC_TERMS)


def _clip(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def fallback_suggestions(
    context: StudentAcademicContext,
) -> InterventionSuggestionsAdvice:
    priority = _priority_for_level(context.risk_level)
    items: list[InterventionSuggestion] = []
    for factor in context.top_factors[:3]:
        label = _FACTOR_LABELS.get(factor.key, factor.key)
        raw = _fmt(factor.raw_value, "%" if factor.unit == "%" else "")
        items.append(
            InterventionSuggestion(
                title=f"Address {label}"[:120],
                description=(
                    f"Plan a short check-in focused on {label} "
                    f"(recorded value {raw})."
                )[:400],
                priority=priority,
                reason=f"This is a leading computed risk factor ({label})."[:300],
            )
        )
    if context.warnings:
        warning = context.warnings[0]
        items.append(
            InterventionSuggestion(
                title="Review early-warning flags"[:120],
                description=warning.message[:400],
                priority="HIGH" if warning.severity == "CRITICAL" else "MEDIUM",
                reason="An early-warning rule has already fired on the facts."[:300],
            )
        )
    if not items:
        items.append(
            InterventionSuggestion(
                title="Schedule a general academic check-in",
                description=(
                    "There is limited academic history. Confirm attendance "
                    "and assessment records, then set a follow-up."
                ),
                priority="MEDIUM",
                reason="Risk data is incomplete; start with visibility.",
            )
        )
    return InterventionSuggestionsAdvice(suggestions=items[:5])


def fallback_chat(question: str, context: StudentAcademicContext) -> ChatAdvice:
    normalized = _normalize_question(question)
    analysis = fallback_analysis(context)
    followups = list(_DEFAULT_FOLLOWUPS)

    if not _is_academic_question(normalized):
        answer = (
            f"{CHAT_UNAVAILABLE} I can only discuss this student's academic "
            "attendance, marks, risk, trends and study habits. Please ask "
            "an academic question."
        )
        return ChatAdvice(answer=_clip(answer), suggested_followups=followups)

    if "why" in normalized and "risk" in normalized:
        answer = f"{CHAT_UNAVAILABLE} {analysis.summary}"
        return ChatAdvice(answer=_clip(answer), suggested_followups=followups)

    if "attend" in normalized:
        attendance = _fmt(context.overall_attendance_percent, "%")
        answer = (
            f"{CHAT_UNAVAILABLE} Overall attendance is {attendance}. "
            "I will not invent a different figure."
        )
        return ChatAdvice(answer=_clip(answer), suggested_followups=followups)

    if "risk" in normalized or "score" in normalized:
        score = _fmt(context.risk_score)
        answer = (
            f"{CHAT_UNAVAILABLE} Risk level is {context.risk_level} "
            f"(risk score of {score})."
        )
        return ChatAdvice(answer=_clip(answer), suggested_followups=followups)

    answer = f"{CHAT_UNAVAILABLE} {analysis.summary}"
    return ChatAdvice(answer=_clip(answer), suggested_followups=followups)
