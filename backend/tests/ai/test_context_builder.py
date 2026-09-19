from tests.ai.helpers import sample_context

from app.ai.context_builder import assert_no_pii


def test_context_has_no_pii() -> None:
    context = sample_context()
    assert_no_pii(
        context,
        forbidden=["Rahul", "rahul@demo.edu", "STU001", "student_id"],
    )
    blob = context.to_prompt_json()
    assert "email" not in blob
    assert "64" in blob
    assert context.risk_level == "HIGH"
