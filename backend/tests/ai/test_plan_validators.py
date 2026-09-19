import json

from app.ai.fallback import fallback_plan
from app.ai.prompts import plan_v1
from app.ai.prompts.plan_v1 import PlanPromptSlot
from app.ai.validators import validate_plan_output


def test_plan_prompt_is_delimited() -> None:
    messages = plan_v1.build_messages(
        [
            PlanPromptSlot(
                slot_id="s1",
                date="2026-09-20",
                subject_code="CS301",
                minutes=60,
                priority="HIGH",
            )
        ],
        {"CS301": ["Trees"]},
    )
    assert "<untrusted_student_data>" in messages[1]["content"]
    assert "plan_v1" == plan_v1.PROMPT_VERSION


def test_unknown_or_missing_slot_is_invalid() -> None:
    expected = ["s1", "s2"]
    codes = {"s1": "CS301", "s2": "CS302"}
    missing = validate_plan_output(
        json.dumps({"slots": [{"slot_id": "s1", "topic": "A", "activity": "B"}]}),
        expected,
        {},
        codes,
    )
    assert not missing.ok
    extra = validate_plan_output(
        json.dumps(
            {
                "slots": [
                    {"slot_id": "s1", "topic": "A", "activity": "B"},
                    {"slot_id": "s2", "topic": "A", "activity": "B"},
                    {"slot_id": "s9", "topic": "A", "activity": "B"},
                ]
            }
        ),
        expected,
        {},
        codes,
    )
    assert not extra.ok


def test_allowed_topic_and_percent_claims() -> None:
    raw = json.dumps(
        {
            "slots": [{"slot_id": "s1", "topic": "Wrong", "activity": "Do work"}],
            "tips": [],
        }
    )
    result = validate_plan_output(
        raw, ["s1"], {"CS301": ["Trees"]}, {"s1": "CS301"}
    )
    assert not result.ok

    grounded = validate_plan_output(
        json.dumps(
            {
                "slots": [
                    {
                        "slot_id": "s1",
                        "topic": "Trees",
                        "activity": "Attendance is 99%.",
                    }
                ]
            }
        ),
        ["s1"],
        {"CS301": ["Trees"]},
        {"s1": "CS301"},
    )
    assert grounded.reason == "UNGROUNDED_OUTPUT"


def test_fallback_uses_template() -> None:
    advice = fallback_plan(
        ["s1"], {"s1": "CS301"}, {"CS301": ["Trees"]}
    )
    assert advice.slots[0].topic == "Trees"
    assert "CS301" in advice.slots[0].activity
    assert "Revise notes and solve 5 practice questions" in advice.slots[0].activity
