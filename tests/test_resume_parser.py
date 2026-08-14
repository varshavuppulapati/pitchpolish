from core.resume_parser import extract_bullets


def test_extract_bullets_filters_short_lines():
    resume_text = (
        "Varsha Vuppulapati\n"
        "varsha@example.com | (555) 555-5555\n"
        "\n"
        "EXPERIENCE\n"
        "• Built a Python audit platform that checks node configurations against baselines.\n"
        "• Led a 7-member team building an AI-driven financial analytics platform.\n"
        "SKILLS\n"
        "Python, Flask, AWS\n"
    )
    bullets = extract_bullets(resume_text)
    assert len(bullets) == 2
    assert bullets[0].startswith("Built a Python audit platform")
    assert bullets[1].startswith("Led a 7-member team")


def test_extract_bullets_strips_bullet_markers():
    resume_text = "- Automated a reporting pipeline that cut runtime by twenty five percent overall"
    bullets = extract_bullets(resume_text)
    assert bullets == ["Automated a reporting pipeline that cut runtime by twenty five percent overall"]


def test_extract_bullets_empty_input():
    assert extract_bullets("") == []
