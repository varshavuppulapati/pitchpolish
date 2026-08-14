from docx import Document

from core.resume_export import build_docx


def test_build_docx_contains_rewritten_bullets():
    rewritten = [
        {"original": "did stuff", "rewritten": "Built a Python audit platform."},
        {"original": "did more stuff", "rewritten": "Led a 7-member Agile team."},
    ]
    buf = build_docx(rewritten, job_title="Software Engineer")

    doc = Document(buf)
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "Built a Python audit platform." in text
    assert "Led a 7-member Agile team." in text
    assert "Software Engineer" in text
