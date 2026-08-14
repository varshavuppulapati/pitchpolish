"""Prompt templates for PitchPolish."""

EXTRACT_KEYWORDS_PROMPT = """You are an expert technical recruiter. Read the job description below and extract the most important skills, tools, and qualifications a strong candidate should highlight.{role_hint}

Classify every keyword into exactly one of these four categories: "Skills" (techniques, competencies, soft skills), "Tools" (specific technologies, languages, platforms), "Experience" (years, seniority, domain background), "Culture" (values, work style, team fit).

Return ONLY a JSON object with this exact shape, no markdown fences, no commentary:
{{
  "must_have": [{{"term": "keyword", "category": "Skills"}}, ...],
  "nice_to_have": [{{"term": "keyword", "category": "Tools"}}, ...]
}}

Keep each term short (1-4 words). Extract at most 12 must_have and 8 nice_to_have keywords, spread across categories as the job description actually warrants (don't force all four if the posting doesn't cover them).

Job description:
---
{job_description}
---
"""

ROLE_HINT_TEMPLATE = " The candidate is targeting a {role} role specifically, so weight keywords relevant to that track higher than tangential ones."

TONE_INSTRUCTIONS = {
    "conservative": "Make minimal changes. Preserve the original phrasing and structure closely, only swapping in job-vocabulary where there's an exact, honest match.",
    "balanced": "Rebalance emphasis and borrow the job's vocabulary where it's a genuine fit, while keeping the sentence recognizably close to the original.",
    "bold": "Confidently reframe the bullet with stronger action verbs and sharper impact framing, while still never inventing facts that aren't in the original.",
}

REWRITE_BULLET_PROMPT = """You are a resume coach. Rewrite the resume bullet below so it speaks more directly to the target job, using the job's own vocabulary where it's a genuine, honest fit.

Rules:
- Never invent numbers, tools, or achievements that aren't in the original bullet.
- Keep it to one sentence, action-verb first.
- Prefer the job description's terminology over synonyms when the meaning matches exactly.
- If the bullet has nothing relevant to borrow from the job description, return it lightly polished but otherwise unchanged.
- Tone: {tone_instruction}

Target job keywords: {keywords}

Original bullet:
{bullet}

Return ONLY the rewritten bullet text, no quotes, no commentary.
"""

COVER_LETTER_PROMPT = """You are a career coach writing a short, honest cover-letter paragraph (not a full letter — just the core pitch paragraph, 4-6 sentences).

Rules:
- Base it only on the resume bullets given below. Never invent achievements, numbers, or tools that aren't listed.
- Reference the job's own language naturally where the candidate's real experience genuinely matches.
- Confident and specific, not generic ("I am a hard worker" energy is banned).
- No greeting ("Dear Hiring Manager") and no sign-off — just the pitch paragraph itself.

Job description:
---
{job_description}
---

Resume bullets:
{bullets}

Return ONLY the paragraph text, no commentary.
"""
