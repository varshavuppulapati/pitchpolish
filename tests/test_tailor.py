from unittest.mock import patch

from core.tailor import compute_radar, extract_keywords, rewrite_bullets, score_match


@patch("core.tailor.chat")
def test_extract_keywords_parses_categorized_json(mock_chat):
    mock_chat.return_value = (
        '{"must_have": [{"term": "Python", "category": "Tools"}, {"term": "5+ years", "category": "Experience"}], '
        '"nice_to_have": [{"term": "Docker", "category": "Tools"}]}'
    )
    result = extract_keywords("some job description")
    assert result["must_have"] == [
        {"term": "Python", "category": "Tools"},
        {"term": "5+ years", "category": "Experience"},
    ]
    assert result["nice_to_have"] == [{"term": "Docker", "category": "Tools"}]


@patch("core.tailor.chat")
def test_extract_keywords_normalizes_plain_string_fallback(mock_chat):
    # Defensive: if the model ever slips back to plain strings, don't crash.
    mock_chat.return_value = '{"must_have": ["Python"], "nice_to_have": []}'
    result = extract_keywords("some job description")
    assert result["must_have"] == [{"term": "Python", "category": "Skills"}]


@patch("core.tailor.chat")
def test_extract_keywords_handles_bad_json(mock_chat):
    mock_chat.return_value = "not json"
    result = extract_keywords("some job description")
    assert result["must_have"] == []
    assert result["nice_to_have"] == []


def _kw(term, category="Skills"):
    return {"term": term, "category": category}


def test_score_match_all_found():
    keywords = {"must_have": [_kw("Python"), _kw("Flask")], "nice_to_have": [_kw("Docker")]}
    resume = "Built a Python service with Flask and deployed it using Docker."
    result = score_match(resume, keywords)
    assert result["score"] == 100
    assert result["must_have_missing"] == []
    assert result["nice_to_have_missing"] == []


def test_score_match_partial():
    keywords = {"must_have": [_kw("Python"), _kw("Kubernetes")], "nice_to_have": []}
    resume = "Built a Python service."
    result = score_match(resume, keywords)
    assert result["must_have_found"] == ["Python"]
    assert result["must_have_missing"] == ["Kubernetes"]
    assert result["score"] == 50


def test_score_match_no_keywords():
    result = score_match("anything", {"must_have": [], "nice_to_have": []})
    assert result["score"] == 0


def test_compute_radar_scores_each_axis():
    keywords = {
        "must_have": [_kw("Python", "Tools"), _kw("Leadership", "Skills")],
        "nice_to_have": [_kw("Docker", "Tools")],
    }
    resume = "Built things with Python and led a team."
    radar = compute_radar(resume, keywords)
    by_axis = {r["axis"]: r["score"] for r in radar}
    assert by_axis["Tools"] == 50  # Python found, Docker missing
    assert by_axis["Skills"] == 100  # Leadership found (case-insensitive substring)
    assert by_axis["Experience"] is None  # no keywords in that category
    assert by_axis["Culture"] is None


def test_compute_radar_covers_all_four_axes():
    radar = compute_radar("anything", {"must_have": [], "nice_to_have": []})
    assert {r["axis"] for r in radar} == {"Skills", "Tools", "Experience", "Culture"}


@patch("core.tailor.chat")
def test_rewrite_bullets_passes_tone_instruction(mock_chat):
    mock_chat.return_value = "Rewritten."
    rewrite_bullets(["Did a thing."], {"must_have": [_kw("Python")], "nice_to_have": []}, tone="bold")
    prompt_arg = mock_chat.call_args[0][0]
    assert "Confidently reframe" in prompt_arg


@patch("core.tailor.chat")
def test_rewrite_bullets_defaults_to_balanced_tone(mock_chat):
    mock_chat.return_value = "Rewritten."
    rewrite_bullets(["Did a thing."], {"must_have": [], "nice_to_have": []})
    prompt_arg = mock_chat.call_args[0][0]
    assert "Rebalance emphasis" in prompt_arg
