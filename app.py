from dotenv import load_dotenv
from flask import Flask, render_template, request

from core.tailor import extract_keywords, rewrite_bullets, score_match

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/tailor", methods=["POST"])
def tailor():
    job_description = request.form.get("job_description", "").strip()
    resume_bullets_raw = request.form.get("resume_bullets", "").strip()
    bullets = [b.strip() for b in resume_bullets_raw.splitlines() if b.strip()]

    error = None
    keywords, match, rewritten = None, None, None

    if not job_description or not bullets:
        error = "Paste both a job description and at least one resume bullet."
    else:
        try:
            keywords = extract_keywords(job_description)
            match = score_match(resume_bullets_raw, keywords)
            rewritten = rewrite_bullets(bullets, keywords)
        except RuntimeError as e:
            error = str(e)
        except Exception as e:
            error = f"Something went wrong talking to the model: {e}"

    return render_template(
        "index.html",
        job_description=job_description,
        resume_bullets=resume_bullets_raw,
        keywords=keywords,
        match=match,
        rewritten=rewritten,
        error=error,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5001)
