import json

from tests.ai.helpers import sample_context

from app.ai.fallback import CHAT_UNAVAILABLE, fallback_chat
from app.ai.prompts import chat_v1
from app.ai.validators import validate_chat_output


def test_chat_prompt_is_delimited() -> None:
    messages = chat_v1.build_messages(
        sample_context(),
        "Why is my risk high?",
        [{"role": "USER", "content": "Hello"}],
    )
    assert chat_v1.PROMPT_VERSION == "chat_v1"
    assert "<untrusted_student_data>" in messages[1]["content"]
    assert "Why is my risk high?" in messages[1]["content"]
    assert "Hello" in messages[1]["content"]


def test_invalid_and_ungrounded_chat() -> None:
    context = sample_context()
    invalid = validate_chat_output("not-json", context)
    assert not invalid.ok
    assert invalid.reason == "INVALID_OUTPUT"

    missing = validate_chat_output(json.dumps({"suggested_followups": []}), context)
    assert not missing.ok

    ungrounded = validate_chat_output(
        json.dumps({"answer": "Attendance is 99%.", "suggested_followups": []}),
        context,
    )
    assert ungrounded.reason == "UNGROUNDED_OUTPUT"

    ok = validate_chat_output(
        json.dumps(
            {
                "answer": f"Risk score of {context.risk_score}.",
                "suggested_followups": ["Next step?"],
            }
        ),
        context,
    )
    assert ok.ok


def test_canned_risk_and_off_topic_fallback() -> None:
    context = sample_context()
    risk = fallback_chat("Why is my risk high?", context)
    assert CHAT_UNAVAILABLE in risk.answer
    assert "HIGH" in risk.answer
    off = fallback_chat("Tell me a joke", context)
    assert "academic" in off.answer.lower()
