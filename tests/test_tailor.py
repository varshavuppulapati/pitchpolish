from unittest.mock import patch

from core.tailor import extract_keywords, score_match


@patch("core.tailor.chat")
def test_extract_keywords_parses_json(mock_chat):
    mock_chat.return_value = '{"must_have": ["Python", "AWS"], "nice_to_have": ["Docker"]}'
    result = extract_keywords("some job description")
    assert result["must_have"] == ["Python", "AWS"]
    assert result["nice_to_have"] == ["Docker"]


@patch("core.tailor.chat")
def test_extract_keywords_handles_bad_json(mock_chat):
    mock_chat.return_value = "not json"
    result = extract_keywords("some job description")
    assert result["must_have"] == []
    assert result["nice_to_have"] == []


def test_score_match_all_found():
    keywords = {"must_have": ["Python", "Flask"], "nice_to_have": ["Docker"]}
    resume = "Built a Python service with Flask and deployed it using Docker."
    result = score_match(resume, keywords)
    assert result["score"] == 100
    assert result["must_have_missing"] == []
    assert result["nice_to_have_missing"] == []


def test_score_match_partial():
    keywords = {"must_have": ["Python", "Kubernetes"], "nice_to_have": []}
    resume = "Built a Python service."
    result = score_match(resume, keywords)
    assert result["must_have_found"] == ["Python"]
    assert result["must_have_missing"] == ["Kubernetes"]
    assert result["score"] == 50


def test_score_match_no_keywords():
    result = score_match("anything", {"must_have": [], "nice_to_have": []})
    assert result["score"] == 0
