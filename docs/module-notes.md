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

## Module 9 — custom function tools (`calculator_agent/`)

A tool is a plain Python function passed to `tools=[...]`; ADK generates the LLM-facing
schema from the **name**, **type hints**, and **docstring** (the docstring is the tool's
API doc *for the model* — highest-leverage part). Return structured data with a `status`
field instead of raising: errors become data the agent can reason about (see `divide` by 0).

## Module 10 — stateful tools via ToolContext (`memory_agent/`)

Declare `tool_context: ToolContext` and ADK injects it (the LLM never sees the param).
`tool_context.state["key"] = value` writes session state as a tracked delta the Runner
persists — exact recall across turns without trusting LLM memory. Use `tool_context.state`,
not `tool_context.session.state` (the raw dict bypasses delta tracking). `output_key` is
the declarative flavor of the same write.

## Module 11 — OpenAPI tools (`market_analyst/`)

Hand an OpenAPI spec to `OpenAPIToolset(spec_str=..., spec_str_type="json")` and each
operation becomes a tool named after its `operationId` — no hand-written HTTP code.
Lab: currency agent over the free Frankfurter API.

## Module 12 — built-in tools & grounding (`research_assistant/`)

`google_search` grounds answers in live web results. Gemini 2+ models can mix built-in
and custom function tools in one agent (older models could not — the module 9 caveat).
The instruction encodes a tool pipeline: search → extract_key_facts → format_research_notes.

## Module 13 — ToolContext.actions & HITL (`secure_finance/`)

"Instructions are just advice" — real security lives in the framework:

- `FunctionTool(fn, require_confirmation=True)`: ADK will not execute the function until
  the user approves the call. A gate the LLM cannot override.
- `tool_context.actions.transfer_to_agent = "supervisor"`: a Python `if` (amount > $10k)
  routes the conversation to a registered sub-agent — enforcement in the runtime, not
  the prompt. Only agents in `sub_agents=[...]` are valid transfer targets.
- `root_agent` here is a `Workflow` graph (`edges=[("START", finance_agent)]`) — first
  taste of Part 3.

## Module 13.5 — custom Firestore persistence (`persistent_agent/`)

Session storage is pluggable: subclass `BaseSessionService` and inject it into
`Runner(app=app, session_service=...)` — the agent code never changes (swap Firestore for
Redis/Postgres the same way). Our `FirestoreSessionService` stores sessions at
`apps/{app}/users/{user}/sessions/{sid}` with events in a sub-collection, and overrides
`append_event` by calling `super().append_event()` first (it applies the state delta and
handles temp-state trimming), then mirroring the event + state to Firestore.

Contract gotchas vs the lab handout: the real ADK 2.7 signature is
`append_event(self, session, event)` (session first), and `get_session` must return `None`
for missing sessions and honor `GetSessionConfig` filters.

Prerequisites to run: Google Cloud CLI, `gcloud auth application-default login`, Firestore
enabled in Native mode, and `GOOGLE_CLOUD_PROJECT` in `.env`. Test: run
`uv run python persistent_agent/main.py "My favorite color is blue."`, kill the process,
run again asking for the color — recall proves persistence.

## Module 14 — third-party tools (`fact_finder_agent/`)

`LangchainTool` (now under `google.adk.integrations.langchain`) adapts any LangChain tool
into an ADK tool — here Wikipedia via `langchain-community` + `wikipedia` packages. One
adapter opens the whole LangChain ecosystem.
