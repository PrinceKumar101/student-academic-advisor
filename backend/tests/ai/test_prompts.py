from tests.ai.helpers import sample_context

from app.ai.prompts import analysis_v1


def test_user_text_is_delimited_as_untrusted() -> None:
    messages = analysis_v1.build_messages(sample_context())
    assert messages[0]["role"] == "system"
    assert "untrusted" in messages[0]["content"].lower()
    user = messages[1]["content"]
    assert "<untrusted_student_data>" in user
    assert "</untrusted_student_data>" in user
    assert "ignore previous" not in user.lower()
