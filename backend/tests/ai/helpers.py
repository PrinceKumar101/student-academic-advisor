import json

from app.ai.context_builder import (
    FactorFact,
    StudentAcademicContext,
    TrendFact,
    build_context,
)


def sample_context() -> StudentAcademicContext:
    return build_context(
        overall_attendance_percent=64.0,
        subject_rows=[],
        risk_score=84.0,
        risk_level="HIGH",
        data_completeness=1.0,
        top_factors=[
            FactorFact(key="attendance", raw_value=64.0, unit="%", risk=65.0),
            FactorFact(key="internal", raw_value=38.0, unit="%", risk=92.5),
        ],
        trends=[
            TrendFact(series="overall", label="DECLINING", first=72.0, last=55.0)
        ],
        warnings=[],
        study_hours_per_day=1.5,
        self_confidence=2,
        extra_factor_keys=[
            "attendance",
            "internal",
            "assignments",
            "quizzes",
            "previous",
            "study_habits",
        ],
    )


def valid_advice_payload(
    context: StudentAcademicContext | None = None,
    *,
    include_numbers: bool = False,
) -> dict:
    context = context or sample_context()
    factor = context.factor_keys[0]
    summary = "The student needs focused support based on the supplied facts."
    if include_numbers and context.risk_score is not None:
        summary = f"The student has a risk score of {context.risk_score}."
    if include_numbers and context.overall_attendance_percent is not None:
        summary += f" Attendance is {context.overall_attendance_percent}%."
    return {
        "summary": summary,
        "main_concerns": [
            {"factor": factor, "explanation": "This factor contributes most to risk."}
        ],
        "recommendations": [
            {
                "action": "Attend remaining scheduled classes.",
                "reason": "Attendance is a supplied risk factor.",
                "priority": "HIGH",
            },
            {
                "action": "Revise weaker subjects first.",
                "reason": "Use the listed weak subjects.",
                "priority": "MEDIUM",
            },
            {
                "action": "Submit pending assignments on time.",
                "reason": "Protect the assignment component.",
                "priority": "MEDIUM",
            },
        ],
        "priority": "HIGH" if context.risk_level == "HIGH" else "MEDIUM",
    }


def valid_advice_json(
    context: StudentAcademicContext | None = None,
    *,
    include_numbers: bool = False,
) -> str:
    return json.dumps(valid_advice_payload(context, include_numbers=include_numbers))
