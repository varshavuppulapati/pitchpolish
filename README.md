# PitchPolish

**[Try it live →](https://pitchpolish.onrender.com)**

Upload your resume (or paste your bullets) and a job posting. Get back a match score, a radar breakdown, a visual keyword bridge, and bullets rewritten to speak the job's language — without inventing anything you didn't do.

*(Free-tier hosting: the first load after a few idle minutes takes 30–50 seconds to wake up.)*

## Features

- **Resume upload** — PDF, DOCX, or TXT, parsed and turned into bullets automatically
- **Match radar chart** — a 4-axis breakdown (Skills / Tools / Experience / Culture), not just one flat score
- **Keyword bridge view** — job posting and resume shown side by side with matched keywords highlighted and visually connected
- **Word-level diff** — rewritten bullets show exactly what changed, not just before/after
- **Drag-to-reorder bullets** — grab the ⠿ handle to prioritize which ones lead
- **Draggable keyword chips** — drag a missing keyword straight onto your resume to add it
- **Tone slider** — live re-rewrite from Conservative to Bold
- **Role presets** — SWE / PM / Data / Design chips bias keyword weighting toward that track
- **Multi-job comparison** — paste up to 3 postings, see a bar chart of which one you already match best
- **Cover letter generator** — one click, grounded in the same tailored bullets
- **DOCX export** of the tailored bullets
- **ATS red-flag checks** — embedded images, likely-scanned PDFs, multi-column layouts, tables
- Mouse-reactive glow, drifting background, a draggable floating score badge, and confetti on results — because a resume tool doesn't have to look like a form

## How it works

1. **Extract** — an LLM reads the job description and pulls out must-have/nice-to-have keywords, each classified into one of four radar axes.
2. **Score** — a deterministic keyword-overlap check compares your resume against those keywords, so the score is fast, free, and reproducible run to run.
3. **Rewrite** — each bullet is rewritten with a strict "don't fabricate" instruction, at whatever tone the slider is set to.

## Run it yourself

```bash
git clone https://github.com/varshavuppulapati/pitchpolish.git
cd pitchpolish
python app.py
```

That's it — no venv, no `pip install`, no `.env` to hand-edit first. The first run installs any missing dependencies automatically and asks for a Groq API key once ([get a free one here](https://console.groq.com/keys), no card required), then saves it to a local `.env` so you're never asked again. Open http://localhost:5001.

## Why Groq instead of OpenAI

Groq's API is OpenAI-SDK-compatible (same `openai` Python package, just a different `base_url`), and its free tier is generous enough to run a public, anyone-can-try-it deployment without turning into a personal expense or an abuse target the way a real OpenAI key would.

## Deploy your own

This repo includes a `render.yaml`, so it deploys to [Render](https://render.com)'s free web service tier in a few clicks: New → Blueprint → point it at this repo → add your `GROQ_API_KEY` in the dashboard → deploy.

## Project structure

```
pitchpolish/
├── app.py                    # Flask routes (JSON API) + startup bootstrap
├── core/
│   ├── setup.py                # Auto-installs deps, prompts + saves API key on first run
│   ├── llm.py                  # Groq (OpenAI-compatible) client wrapper
│   ├── prompts.py              # Prompt templates (keywords, rewriting, cover letter)
│   ├── tailor.py                # Keyword extraction, scoring, radar, rewriting
│   ├── resume_parser.py        # PDF/DOCX/TXT text extraction + bullet detection
│   ├── resume_export.py        # DOCX export of tailored bullets
│   └── ats_check.py            # ATS red-flag heuristics
├── templates/index.html
├── static/{style.css, app.js}  # Drag-and-drop, radar chart, keyword bridge, animations
├── tests/
├── requirements.txt
├── render.yaml
└── .env.example
```

## Why the score isn't an LLM call

Keyword matching is deterministic and free. Asking an LLM to "score this resume from 1–100" produces numbers that drift between runs on identical input, which makes the score useless for tracking whether a rewrite actually helped. Extraction and rewriting benefit from an LLM's judgment; scoring doesn't need it.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

Tests mock the model call, so they run without an API key.

## License

MIT — see [LICENSE](LICENSE).
