# Setup

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), a Google API key ([AI Studio](https://aistudio.google.com/apikey)) or a GCP project.

```sh
uv sync
copy .env.example .env   # then paste your GOOGLE_API_KEY into .env
```

## Authentication options

**Option A — API key (beginners).** Set in `.env`:

```
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your-api-key-here
```

**Option B — Vertex AI (enterprise).** Uses Application Default Credentials via the Google Cloud CLI (`gcloud auth application-default login`):

```
GOOGLE_GENAI_USE_VERTEXAI=1
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
```

## Working with uv

- Add dependencies with `uv add <pkg>` (never bare `pip install` — that hits whatever Python is on PATH, e.g. Anaconda, not this project).
- Run everything through `uv run ...` so it executes inside the project venv on the pinned Python (`.python-version` → 3.11; uv downloads the interpreter if missing).
- `uv.lock` pins the full dependency tree — commit it; `uv sync` reproduces the exact environment on any machine.

## Verify the environment

```sh
uv run python verify_setup.py
```

Prints `SETUP COMPLETE! You are running ADK 2.0.` when the model answers.

## Model name gotcha

Lab snippets use `gemini-2.5-flash` / `gemini-3.5-flash`, which 404 for new API keys
(`This model is no longer available to new users`). Use **`gemini-3.6-flash`** — check
every pasted lab snippet.
