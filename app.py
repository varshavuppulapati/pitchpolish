from core.setup import ensure_api_key, ensure_dependencies

ensure_dependencies()
ensure_api_key()

import json  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

from flask import Flask, jsonify, render_template, request, send_file  # noqa: E402

from core.ats_check import check_ats_issues  # noqa: E402
from core.resume_export import build_docx  # noqa: E402
from core.resume_parser import extract_bullets, extract_text  # noqa: E402
from core.tailor import compute_radar, extract_keywords, generate_cover_letter, rewrite_bullets, score_match  # noqa: E402

app = Flask(__name__)

ALLOWED_RESUME_EXT = {".pdf", ".docx", ".txt"}
MAX_BULLETS = 12  # keeps a full resume upload from triggering dozens of LLM calls
MAX_COMPARE_JOBS = 3


@app.errorhandler(Exception)
def handle_uncaught_error(e):
    """Guarantees /api/* always returns JSON, even on a bug we didn't anticipate -
    otherwise Flask's default HTML error page breaks the frontend's res.json()."""
    if request.path.startswith("/api/"):
        return jsonify(error=f"Unexpected server error: {e}"), 500
    raise e


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


def _resolve_resume(pasted_bullets_raw, resume_file):
    """Returns (resume_text, bullets, ats_issues, error_response_or_None)."""
    resume_text = pasted_bullets_raw
    bullets = [b.strip() for b in pasted_bullets_raw.splitlines() if b.strip()]
    ats_issues = []

    if resume_file and resume_file.filename:
        ext = os.path.splitext(resume_file.filename)[1].lower()
        if ext not in ALLOWED_RESUME_EXT:
            return None, None, None, (jsonify(error=f"Unsupported resume file type: {ext}"), 400)
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            resume_file.save(tmp.name)
            tmp_path = tmp.name
        try:
            resume_text = extract_text(tmp_path)
            bullets = extract_bullets(resume_text)
            ats_issues = check_ats_issues(tmp_path, resume_text)
        finally:
            os.unlink(tmp_path)

    if not bullets:
        return None, None, None, (jsonify(error="Paste your resume bullets or upload a resume file with some in it."), 400)

    return resume_text, bullets[:MAX_BULLETS], ats_issues, None


@app.route("/api/tailor", methods=["POST"])
def api_tailor():
    job_description = request.form.get("job_description", "").strip()
    role_hint = request.form.get("role_hint", "").strip() or None
    tone = request.form.get("tone", "balanced")
    pasted_bullets_raw = request.form.get("resume_bullets", "").strip()
    resume_file = request.files.get("resume_file")

    if not job_description:
        return jsonify(error="Paste a job description first."), 400

    resume_text, bullets, ats_issues, err = _resolve_resume(pasted_bullets_raw, resume_file)
    if err:
        return err

    try:
        keywords = extract_keywords(job_description, role_hint=role_hint)
        match = score_match(resume_text, keywords)
        radar = compute_radar(resume_text, keywords)
        rewritten = rewrite_bullets(bullets, keywords, tone=tone)
    except RuntimeError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=f"Something went wrong talking to the model: {e}"), 500

    return jsonify(
        keywords=keywords,
        match=match,
        radar=radar,
        rewritten=rewritten,
        resume_text=resume_text,
        job_description=job_description,
        ats_issues=ats_issues,
    )


@app.route("/api/cover-letter", methods=["POST"])
def api_cover_letter():
    job_description = request.form.get("job_description", "").strip()
    bullets_raw = request.form.get("bullets", "[]")
    try:
        bullets = [b["rewritten"] for b in json.loads(bullets_raw)]
    except (ValueError, KeyError, TypeError):
        return jsonify(error="Missing or malformed bullets."), 400

    if not job_description or not bullets:
        return jsonify(error="Tailor your resume first, then generate a cover letter."), 400

    try:
        letter = generate_cover_letter(job_description, bullets)
    except RuntimeError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=f"Something went wrong talking to the model: {e}"), 500

    return jsonify(letter=letter)


@app.route("/api/compare", methods=["POST"])
def api_compare():
    jobs_raw = request.form.get("jobs", "[]")
    pasted_bullets_raw = request.form.get("resume_bullets", "").strip()
    resume_file = request.files.get("resume_file")

    try:
        jobs = [j.strip() for j in json.loads(jobs_raw) if j.strip()]
    except ValueError:
        return jsonify(error="Malformed job list."), 400
    jobs = jobs[:MAX_COMPARE_JOBS]
    if len(jobs) < 2:
        return jsonify(error="Add at least two job postings to compare."), 400

    resume_text, bullets, _ats_issues, err = _resolve_resume(pasted_bullets_raw, resume_file)
    if err:
        return err

    try:
        def _score_one(job_description):
            keywords = extract_keywords(job_description)
            return score_match(resume_text, keywords)["score"]

        with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            scores = list(pool.map(_score_one, jobs))
        results = [{"label": f"Job {i + 1}", "score": s} for i, s in enumerate(scores)]
    except RuntimeError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=f"Something went wrong talking to the model: {e}"), 500

    return jsonify(results=results)


@app.route("/api/export", methods=["POST"])
def api_export():
    rewritten_raw = request.form.get("rewritten", "[]")
    try:
        rewritten = json.loads(rewritten_raw)
    except ValueError:
        return jsonify(error="Malformed bullet list."), 400
    if not rewritten:
        return jsonify(error="Tailor your resume first."), 400

    try:
        buf = build_docx(rewritten)
    except Exception as e:
        return jsonify(error=f"Couldn't build the DOCX: {e}"), 500

    return send_file(
        buf,
        as_attachment=True,
        download_name="tailored-resume.docx",
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
