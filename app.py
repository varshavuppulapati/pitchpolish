from core.setup import ensure_api_key, ensure_dependencies

ensure_dependencies()
ensure_api_key()

import os  # noqa: E402
import tempfile  # noqa: E402

from flask import Flask, jsonify, render_template, request  # noqa: E402

from core.resume_parser import extract_bullets, extract_text  # noqa: E402
from core.tailor import extract_keywords, rewrite_bullets, score_match  # noqa: E402

app = Flask(__name__)

ALLOWED_RESUME_EXT = {".pdf", ".docx", ".txt"}
MAX_BULLETS = 12  # keeps a full resume upload from triggering dozens of LLM calls


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/api/tailor", methods=["POST"])
def api_tailor():
    job_description = request.form.get("job_description", "").strip()
    pasted_bullets_raw = request.form.get("resume_bullets", "").strip()
    resume_file = request.files.get("resume_file")

    if not job_description:
        return jsonify(error="Paste a job description first."), 400

    resume_text = pasted_bullets_raw
    bullets = [b.strip() for b in pasted_bullets_raw.splitlines() if b.strip()]

    try:
        if resume_file and resume_file.filename:
            ext = os.path.splitext(resume_file.filename)[1].lower()
            if ext not in ALLOWED_RESUME_EXT:
                return jsonify(error=f"Unsupported resume file type: {ext}"), 400
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
                resume_file.save(tmp.name)
                tmp_path = tmp.name
            try:
                resume_text = extract_text(tmp_path)
            finally:
                os.unlink(tmp_path)
            bullets = extract_bullets(resume_text)

        if not bullets:
            return jsonify(error="Paste your resume bullets or upload a resume file with some in it."), 400

        bullets = bullets[:MAX_BULLETS]

        keywords = extract_keywords(job_description)
        match = score_match(resume_text, keywords)
        rewritten = rewrite_bullets(bullets, keywords)
    except RuntimeError as e:
        return jsonify(error=str(e)), 500
    except Exception as e:
        return jsonify(error=f"Something went wrong talking to the model: {e}"), 500

    return jsonify(keywords=keywords, match=match, rewritten=rewritten, resume_text=resume_text)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
