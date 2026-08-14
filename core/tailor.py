"""Core matching + rewriting logic for PitchPolish."""
import json
import re

from .llm import chat
from .prompts import (
    COVER_LETTER_PROMPT,
    EXTRACT_KEYWORDS_PROMPT,
    REWRITE_BULLET_PROMPT,
    ROLE_HINT_TEMPLATE,
    TONE_INSTRUCTIONS,
)

RADAR_AXES = ["Skills", "Tools", "Experience", "Culture"]


def _strip_code_fence(raw):
    return re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()


def _normalize_keyword_list(raw_list):
    """Accepts either the new [{"term","category"}] shape or a plain list of
    strings (defensive, in case the model ever slips back to the old shape)."""
    normalized = []
    for item in raw_list or []:
        if isinstance(item, dict):
            term = str(item.get("term", "")).strip()
            category = item.get("category") if item.get("category") in RADAR_AXES else "Skills"
        else:
            term, category = str(item).strip(), "Skills"
        if term:
            normalized.append({"term": term, "category": category})
    return normalized


def extract_keywords(job_description, role_hint=None):
    hint = ROLE_HINT_TEMPLATE.format(role=role_hint) if role_hint else ""
    raw = chat(EXTRACT_KEYWORDS_PROMPT.format(job_description=job_description, role_hint=hint))
    raw = _strip_code_fence(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    return {
        "must_have": _normalize_keyword_list(data.get("must_have")),
        "nice_to_have": _normalize_keyword_list(data.get("nice_to_have")),
    }


def score_match(resume_text, keywords):
    """Deterministic keyword-overlap score. No LLM call, so it's fast, free, and reproducible."""
    resume_lower = resume_text.lower()
    must_have = keywords.get("must_have", [])
    nice_to_have = keywords.get("nice_to_have", [])

    def split_hits(items):
        found, missing = [], []
        for item in items:
            (found if item["term"].lower() in resume_lower else missing).append(item["term"])
        return found, missing

    must_found, must_missing = split_hits(must_have)
    nice_found, nice_missing = split_hits(nice_to_have)

    total = len(must_have) * 2 + len(nice_to_have)
    earned = len(must_found) * 2 + len(nice_found)
    score = round((earned / total) * 100) if total else 0

    return {
        "score": score,
        "must_have_found": must_found,
        "must_have_missing": must_missing,
        "nice_to_have_found": nice_found,
        "nice_to_have_missing": nice_missing,
    }


def compute_radar(resume_text, keywords):
    """Per-category (Skills/Tools/Experience/Culture) match percentage, for the radar chart."""
    resume_lower = resume_text.lower()
    all_items = keywords.get("must_have", []) + keywords.get("nice_to_have", [])

    radar = []
    for axis in RADAR_AXES:
        axis_items = [i for i in all_items if i["category"] == axis]
        if not axis_items:
            radar.append({"axis": axis, "score": None})
            continue
        found = sum(1 for i in axis_items if i["term"].lower() in resume_lower)
        radar.append({"axis": axis, "score": round((found / len(axis_items)) * 100)})
    return radar


def rewrite_bullets(bullets, keywords, tone="balanced"):
    all_terms = [i["term"] for i in keywords.get("must_have", []) + keywords.get("nice_to_have", [])]
    keyword_str = ", ".join(all_terms) if all_terms else "no specific keywords found"
    tone_instruction = TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["balanced"])

    rewritten = []
    for bullet in bullets:
        bullet = bullet.strip()
        if not bullet:
            continue
        new_bullet = chat(
            REWRITE_BULLET_PROMPT.format(keywords=keyword_str, bullet=bullet, tone_instruction=tone_instruction)
        )
        rewritten.append({"original": bullet, "rewritten": new_bullet})
    return rewritten


def generate_cover_letter(job_description, bullets):
    bullets_str = "\n".join(f"- {b}" for b in bullets)
    return chat(
        COVER_LETTER_PROMPT.format(job_description=job_description, bullets=bullets_str),
        temperature=0.5,
    )
