# Module notes

Lessons worth keeping from each lab.

## Module 4 — agent config: structured output

`output_schema=<PydanticModel>` forces the agent to reply with JSON matching the schema;
`output_key="..."` additionally saves the parsed result into session state (visible in the
dev UI **State** tab).

## Module 4.5 — model switching

Pick the model object once via an env toggle, keep the agent definition identical:

- `USE_LOCAL_MODEL=1` → `LiteLlm(model="ollama_chat/mistral")` (requires Ollama running
  with the model pulled; small local models honor `output_schema` less reliably).
- otherwise → `ResilientGemini`, a `Gemini` subclass whose `api_client` centralizes retry
  options (exponential backoff + jitter).

Gotchas:

- The toggle is evaluated at **import time** — restart `adk web` after changing `.env`.
- `Client(project=..., location=...)` is only legal in Vertex AI mode (`vertexai=True`).
  In API-key mode, build a bare `Client(http_options=...)` — it reads `GOOGLE_API_KEY`.

## Module 6 — programmatic execution: `print` vs `logging`

`print` is for a script's *output* (the thing the user asked for — fine in lab demos like
`support_analyzer/main.py`); `logging` is for *diagnostics*, and is what production code uses:

- **Levels** (`debug`/`info`/`warning`/`error`) — change verbosity via config, not code edits.
- **Context for free** — timestamps, module name, full tracebacks with `logger.exception(e)`.
- **Destinations** — stderr, rotating files, or Cloud Logging by swapping handlers at startup.
- **Per-module filtering** — silence a chatty library while keeping your own debug logs.
- **Observability** — ADK logs through this system; leveled logs are what make Cloud Run's
  Logs Explorer useful once we deploy (Part 6 of the course).

The idiom — a named logger per module, configured once in the entrypoint:

```python
# top of any module
import logging
logger = logging.getLogger(__name__)

# entrypoint (main.py) only
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# usage — pass values as args (lazy formatting), not f-strings
logger.info("Session created for user %s", user_id)
logger.debug("Raw model JSON: %s", response_text)
```

Also from this module: the **Runner** is ADK's runtime engine — it loads the session,
appends the message, drives the agent (LLM + tools), streams events, and persists state.
`InMemoryRunner` is a `Runner` with in-RAM session/artifact/memory services: zero setup,
nothing survives a restart. Production swaps in persistent services, same runner concept.

## Module 7 — multimodal: images as message parts

An image is just another `Part` in the user `Content`:

```python
types.Content(role="user", parts=[
    types.Part(text="Describe this product."),
    types.Part(inline_data=types.Blob(data=image_bytes, mime_type="image/jpeg")),
])
```

The lab (`visual_catalog/`) is a standalone script: the agent is built in code and driven
by `runner.run_async()` — no CLI discovery involved. `run_async` requires the session to
exist first (`session_service.create_session(...)`), unlike the `run_debug` helper.

Transient `503 UNAVAILABLE` ("high demand") errors are the server shedding load — retry;
this is exactly what module 4.5's retry options are for. Multimodal requests are heavier
and more likely to be shed, and free-tier keys are shed first.
