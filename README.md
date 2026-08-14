# PitchPolish

Paste a job posting and your resume bullets. PitchPolish extracts the job's must-have and nice-to-have keywords, scores how well your resume already matches, and rewrites each bullet to speak the job's language — without inventing anything you didn't actually do.

## How it works

1. **Extract** — an LLM call reads the job description and pulls out must-have and nice-to-have keywords as structured JSON.
2. **Score** — a deterministic (non-LLM) keyword-overlap check compares your resume text against those keywords, so the score is fast, free, and reproducible run to run.
3. **Rewrite** — each resume bullet is rewritten with a strict "don't fabricate" instruction: it can reorder emphasis and borrow the job's vocabulary, but it can't invent numbers, tools, or achievements you didn't list.

## Setup

```bash
git clone https://github.com/varshavuppulapati/pitchpolish.git
cd pitchpolish
python app.py
```

That's it — no venv, no `pip install`, no `.env` to hand-edit first. The first run installs any missing dependencies automatically and asks for a Groq API key once ([get a free one here](https://console.groq.com/keys), no card required), then saves it to a local `.env` so you're never asked again.

Open http://localhost:5001, paste a job description and your bullets (one per line), and hit **Tailor my resume**.

## Why Groq instead of OpenAI

Groq's API is OpenAI-SDK-compatible (same `openai` Python package, just a different `base_url`), and its free tier is generous enough to run a public, anyone-can-try-it deployment without turning into a personal expense or an abuse target the way a real OpenAI key would.

## Deploy your own

This repo includes a `render.yaml`, so it deploys to [Render](https://render.com)'s free web service tier in a few clicks: New → Blueprint → point it at this repo → add your `GROQ_API_KEY` in the dashboard → deploy.

## Project structure

```
pitchpolish/
├── app.py                  # Flask routes + startup bootstrap
├── core/
│   ├── setup.py              # Auto-installs deps, prompts + saves API key on first run
│   ├── llm.py                # Groq (OpenAI-compatible) client wrapper
│   ├── prompts.py            # Prompt templates
│   └── tailor.py             # Keyword extraction, scoring, rewriting
├── templates/index.html
├── static/style.css
├── tests/test_tailor.py
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

## License

MIT — see [LICENSE](LICENSE).
