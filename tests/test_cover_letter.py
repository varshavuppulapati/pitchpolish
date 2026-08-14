from unittest.mock import patch

from core.tailor import generate_cover_letter


@patch("core.tailor.chat")
def test_generate_cover_letter_passes_bullets_and_job(mock_chat):
    mock_chat.return_value = "A tailored pitch paragraph."
    result = generate_cover_letter("Looking for a Python engineer.", ["Built a Python audit platform."])
    assert result == "A tailored pitch paragraph."
    prompt_arg = mock_chat.call_args[0][0]
    assert "Looking for a Python engineer." in prompt_arg
    assert "Built a Python audit platform." in prompt_arg


@patch("core.tailor.chat")
def test_extract_keywords_with_role_hint_includes_it_in_prompt(mock_chat):
    mock_chat.return_value = '{"must_have": [], "nice_to_have": []}'
    from core.tailor import extract_keywords

    extract_keywords("some job", role_hint="Data / ML")
    prompt_arg = mock_chat.call_args[0][0]
    assert "Data / ML" in prompt_arg
