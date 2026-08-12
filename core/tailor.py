"""Core matching + rewriting logic for PitchPolish."""
import json
import re

from .llm import chat
from .prompts import EXTRACT_KEYWORDS_PROMPT, REWRITE_BULLET_PROMPT


def _strip_code_fence(raw):
    return re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()


def extract_keywords(job_description):
    raw = chat(EXTRACT_KEYWORDS_PROMPT.format(job_description=job_description))
    raw = _strip_code_fence(raw)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}
    data.setdefault("must_have", [])
    data.setdefault("nice_to_have", [])
    return data


def score_match(resume_text, keywords):
    """Deterministic keyword-overlap score. No LLM call, so it's fast, free, and reproducible."""
    resume_lower = resume_text.lower()
    must_have = keywords.get("must_have", [])
    nice_to_have = keywords.get("nice_to_have", [])

    def split_hits(words):
        found, missing = [], []
        for w in words:
            (found if w.lower() in resume_lower else missing).append(w)
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


def rewrite_bullets(bullets, keywords):
    all_keywords = keywords.get("must_have", []) + keywords.get("nice_to_have", [])
    keyword_str = ", ".join(all_keywords) if all_keywords else "no specific keywords found"

    rewritten = []
    for bullet in bullets:
        bullet = bullet.strip()
        if not bullet:
            continue
        new_bullet = chat(REWRITE_BULLET_PROMPT.format(keywords=keyword_str, bullet=bullet))
        rewritten.append({"original": bullet, "rewritten": new_bullet})
    return rewritten
