"""Extracts plain text from an uploaded resume file (PDF, DOCX, or plain text)."""
import os


def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return _extract_pdf(file_path)
    if ext == ".docx":
        return _extract_docx(file_path)
    if ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Unsupported resume file type: {ext}")


def _extract_pdf(file_path):
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(file_path):
    from docx import Document

    doc = Document(file_path)
    return "\n".join(p.text for p in doc.paragraphs)


def extract_bullets(resume_text):
    """Heuristic: real resume bullets tend to be full sentences/phrases, not
    short header or contact-info lines, so filter on length and word count."""
    bullets = []
    for line in resume_text.splitlines():
        line = line.strip().lstrip("•-*▪◦●○►▶\t ").strip()
        if len(line) < 20 or line.count(" ") < 3:
            continue
        bullets.append(line)
    return bullets
