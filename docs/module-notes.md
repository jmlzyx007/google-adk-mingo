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

## Module 15 — intro to multi-agent systems (`greeting_system/`)

First real multi-agent lab: a **router** LLM delegates to a **specialist** sub-agent.

- Registering `sub_agents=[...]` auto-injects a `transfer_to_agent` tool into the parent;
  the router's LLM sees each sub-agent's **name + description** and decides when to hand
  off. The `description` is the specialist's advertisement to its parent — routing quality
  lives there (module 9's docstring lesson, applied to agents).
- After a transfer, the specialist answers the user **directly** — the router is out of
  the loop for that turn.
- Unsupported requests (French) are handled by the router itself per its instruction —
  delegation is a choice, not a requirement.
- `root_agent` is a `Workflow` graph (`edges=[("START", router)]`) — the module 13
  preview becomes the standard shape for Part 3.

Verified live: "greet me in Spanish" → `TRANSFER -> spanish_greeter_agent` → answer in
Spanish; "greet me in French" → router politely declines without transferring.

## Module 16 — static orchestration (`news_aggregator/`)

Opposite of module 15: the graph is **fixed at build time**, no LLM routing decisions.

```
START ─┬─> tech_researcher ──┐
       │                     ├─> news_sync (JoinNode) ─> summarizer
       └─> market_researcher ┘
```

- Two edges from `START` = **parallel fan-out**: both researchers run concurrently.
- `JoinNode` is the barrier — downstream doesn't start until every incoming branch is done.
- Data flows between agents through **session state**: researchers write via
  `output_key="tech_news"` / `"market_news"`; the summarizer reads them with `{tech_news}`
  / `{market_news}` placeholders in its instruction (interpolated from state at call time).
- Edge tuples support path shorthand: `("START", agent, syncer)` = two edges.

Verified live: event order tech → market → join → summarizer; both state keys present;
coherent merged briefing. Note: parallel fan-out doubles simultaneous requests — free-tier
keys hit 503 load-shedding more often (retry, or see the model fallbacks in setup notes).

## Module 17 — structured routing (`market_router/`)

Middle ground between modules 15 and 16: the **LLM classifies, the graph routes**.

```
START ─> classifier ─> route_currency ─┬─ "USD" ─> usd_analyst
                                       ├─ "EUR" ─> eur_analyst
                                       └─ "GBP" ─> gbp_analyst
```

- The classifier's `output_schema` uses `Literal["USD", "EUR", "GBP"]` — the schema
  *constrains* the decision space, so routing can't receive an unexpected value.
- A **dictionary edge** `(node, {"USD": usd_analyst, ...})` creates one conditional edge
  per key; the workflow follows the edge matching the node's emitted route.
- **ADK 2.7 gotcha (deviation from the lab handout):** an LlmAgent node puts its validated
  schema object on `ctx.output`, but dict edges match on `ctx.route` — nothing derives one
  from the other, so the branch silently dies ("none were matched by the emitted route(s):
  None"). Bridge with a tiny `@node` function that reads the upstream output (`node_input`)
  and sets `ctx.route`. `DEFAULT_ROUTE` exists for fallback edges.

Verified live: dollar/euro/pound questions each reached their own analyst.

Routing spectrum so far: **15** = LLM decides freely (`sub_agents` transfer),
**17** = LLM decides within a schema, graph executes, **16** = no decisions at all.

## Module 18 — dynamic orchestration (`support_router_v2/`)

The graph becomes a **program**: an async `@node` orchestrator drives sub-nodes with plain
Python instead of declared edges.

```python
@node(rerun_on_resume=True)
async def support_router_workflow(ctx: Context, node_input: str):
    result = await ctx.run_node(classifier, node_input)      # run an agent, get its result
    classification = SentimentClassification.model_validate(result)
    chosen = human_escalation if classification.sentiment == "angry" else ai_support
    return await ctx.run_node(chosen, node_input)
```

- `await ctx.run_node(agent_or_node, input)` executes any NodeLike as a child run and
  returns its result directly — no state plumbing, no route emission. Always `await` it
  (never `asyncio.create_task` — errors get swallowed and HITL cancellation breaks).
- Any Python control flow works: if/else, loops, retries, try/except around sub-agents.
- `rerun_on_resume=True`: on resume after a pause, the orchestrator function re-executes
  from the top (completed child runs replay from cache), so the routing logic re-evaluates.
- **ADK 2.7 gotcha:** `ctx.run_node` returns structured output as a plain **dict**, not
  the pydantic instance — `model_validate` it back for typed access.

Verified live: angry data-loss rant → `human_escalation_team` apology; neutral how-to
question → `ai_support_bot` answer.

Orchestration ladder complete: 16 static edges → 17 schema-routed edges → 18 code.

## Module 19 — collaborative teams: modes & hand-offs (`travel_team/`)

A coordinator `Agent` (not a Workflow) with moded sub-agents. `mode` makes the
return-to-parent contract deterministic instead of trusting the LLM to remember:

- `mode="single_turn"` — answer once, control returns to the parent. No user interaction
  (right for pure data retrieval, e.g. `weather_checker`).
- `mode="task"` — may ask the user clarifying questions until its objective completes,
  then returns to the parent (e.g. `flight_booker`).
- coordinator (no mode) — owns the conversation, delegates, synthesizes.

**ADK 2.7 gotchas found live:**

- The **dispatching parent** needs `rerun_on_resume=True` — moded sub-agents are
  dynamically scheduled nodes; if one is interrupted, the parent re-runs on wake-up to
  collect the child's response. Without it: `ValueError: A node must have
  rerun_on_resume=True` on the first hand-off.
- A `task` agent that asks the user a question puts the run into a WAITING state that the
  dev UI resumes natively. A plain scripted `run_async` loop does not route the next
  message back into the waiting task — **test interactive task-mode flows in `adk web`**,
  script only the non-interactive paths.
- Production tip from the runtime warning: apps that transfer between agents should set
  `context_cache_config` — every hand-off swaps system prompt + tools, so without per-agent
  caching the full prompt is re-sent uncached after each transfer.

## Module 20 — cyclic workflows: iteration & self-correction (`essay_refiner/`)

A write → critique → refine cycle inside a dynamic `@node` orchestrator:

```python
current_story = await ctx.run_node(writer, node_input)
for _ in range(MAX_ITERATIONS):                    # hard stop — non-negotiable
    feedback = await ctx.run_node(critic, current_story)
    if "APPROVED" in str(feedback):                # semantic exit
        break
    current_story = await ctx.run_node(refiner, f"STORY...{feedback}")
return current_story
```

- **Two exit conditions, both mandatory**: the semantic one (critic approves) and the hard
  cap (`range(3)`). LLMs are non-deterministic — a never-satisfied critic without the cap
  means an infinite loop and unbounded API cost. Verified both paths live: a lenient critic
  approved on round 1; a strict critic never approved and the cap ended it after 3 rounds.
- The loop state (`current_story`) is just a Python variable — no session-state plumbing.
- **Output vs last message:** the orchestrator's `return` value travels on `event.output`;
  the last *content* message the user-facing stream sees is whatever the last child said
  (e.g. the critic's "APPROVED"). When scripting, read `event.output` for the result.
- Lab-handout fixes for ADK 2.7: `@node(rerun_on_resume=True)` (dispatching parents need
  it), positional `ctx.run_node(agent, input)` (no `input=` kwarg), and pass data in the
  input string rather than `{placeholders}` (those interpolate from session state).

## Module 21 — distributed graphs: A2A (`research_specialist/` + `a2a_orchestrator/`)

Agents in **separate processes** (or machines, or Cloud Run services) composed into one
system via the A2A protocol — "graph of graphs".

- **Server side:** `to_a2a(root_agent, port=8001)` wraps a normal agent as an ASGI app.
  Serve it with `uv run uvicorn research_specialist.agent:a2a_app --port 8001`. It
  publishes an **agent card** at `/.well-known/agent-card.json` (name, description,
  skills, protocol bindings) — the discovery contract.
- **Client side:** `RemoteA2aAgent(name=..., agent_card="http://host:8001<CARD_PATH>")`
  makes the remote agent look like a local sub-agent — the coordinator delegates to it
  with the same `sub_agents` mechanism as module 15; the network is fully abstracted.
- Needs extras: `uv add "google-adk[a2a]" sse-starlette` (the a2a-sdk server routes
  import sse_starlette but the extra doesn't pull it).
- ADK's A2A implementation is marked EXPERIMENTAL (the protocol itself is stable).
- Lab-handout fix: `GoogleSearchAgentTool` doesn't exist in ADK 2.7 — use the
  `google_search` built-in.

Verified live: card served on port 8001; orchestrator in a second process transferred to
`remote_researcher` over HTTP and returned a live-researched, current answer.

## Module 21.5 — MAS knowledge milestone: architecture choice

Decision framework consolidating Part 3:

| Pattern | Module | Use when |
|---|---|---|
| Static orchestration | 16 | Fixed pipeline, parallel steps, join points |
| Structured routing | 17 | Bounded branching on a classified value |
| Dynamic orchestration | 18 | Loops, retries, data-dependent control flow |
| Collaborative teams | 19 | Conversational hand-offs, specialist sub-dialogues |
| Cyclic workflows | 20 | Iterative refinement with quality gate + hard cap |
| Distributed graphs | 21 | Separate environments, independent scaling/teams |

Three-question heuristic: path predictable? → static/structured edges. Needs Python
control flow? → dynamic `@node`. Needs separate environments? → distributed A2A.
No one-size-fits-all — production systems are hybrids; prefer the simplest pattern that
fits, and validate the design in the dev UI's graph view.

## Module 22 — state scopes & memory (`personal_tutor/`)

One state dict, four scopes decided purely by **key prefix**:

| Prefix | Scope | Verified behavior |
|---|---|---|
| `user:` | all sessions of this user (per app) | visible in a brand-new session before any turn |
| *(none)* | this session only | `current_topic` never appeared in session 2 |
| `temp:` | this invocation only | written by the grade tool, absent from persisted state |
| `app:` | every user of the app | global config, e.g. set via dev UI State tab |

- Same `tool_context.state[...]` API for all scopes — the prefix does the routing
  (base session service applies `user:`/`app:` deltas to the right stores and trims
  `temp:` before persisting; we saw that code in module 13.5's `append_event`).
- **Instruction injection**: `{user:language}` / `{app:course_version?}` placeholders in
  the instruction interpolate from state; `?` makes a placeholder optional (no error when
  unset) — use it for keys that may not exist yet.
- Copy-on-read gotcha: mutate list/dict state via read → copy → reassign
  (`topics = list(state.get(...)); ...; state[k] = topics`) so the write is a tracked delta.
- `InMemorySessionService` keeps `user:`/`app:` across sessions but loses everything on
  process restart — production needs a persistent SessionService (module 13.5) plus a
  semantic memory service (`VertexAiMemoryBankService`) instead of the simulated
  `search_past_lessons`.

## Module 23 — artifacts (`doc_processor/`)

State holds small key-value data; **artifacts hold files** — text or binary `types.Part`s
stored by filename with automatic versioning. Third pluggable service on the Runner
(sessions / memory / artifacts): `InMemoryArtifactService` for dev,
`GcsArtifactService(bucket_name=...)` in production — tool code identical.

```python
version = await tool_context.save_artifact(name, part)   # returns version int (0, 1, ...)
part    = await tool_context.load_artifact(name)          # latest, or version=n
names   = await tool_context.list_artifacts()
```

- All artifact methods are **async** — tools that touch them must be `async def`.
- `types.Part.from_text(text=...)` for text, `types.Part.from_bytes(data=..., mime_type=...)`
  for binary; on load, check `part.text` vs `part.inline_data` (mime_type + data).
- Every save creates a **new version** (audit trail for free); `load_artifact(version=n)`
  reads history.
- Lab: 4-stage pipeline (extract → summarize → chart → report) where each stage's output
  is the next stage's input via artifacts, and the report compiles them via
  `list_artifacts()`. Verified live: 4 artifacts stored, PNG kept its mime type, report
  aggregated text + binary correctly.

## Module 24 — evaluation (`calculator_agent/calculator_tests.evalset.json`)

Agent testing formalized: an **evalset** (JSON) of cases — user prompt, expected final
response, expected **tool trajectory** (calls + args) — replayed live by:

```sh
uv run adk eval calculator_agent calculator_agent/calculator_tests.evalset.json \
    --config_file_path calculator_agent/test_config.json --print_detailed_results
```

- Two metrics (thresholds in `test_config.json`): `tool_trajectory_avg_score` — exact
  match on tool calls/args, keep at **1.0** (the robust signal: verifies the reasoning
  path, not lucky text); `response_match_score` — ROUGE text overlap vs the golden answer.
- Needs `google-adk[eval]` extra — which pins `litellm<1.86` (conflicts with newer litellm;
  we downgraded 1.97 → 1.85.7).
- Results land in `<agent>/.adk/eval_history/*.evalset_result.json`; the dev UI Eval tab
  can record cases from live sessions and re-run them.
- Schema classes (`google.adk.evaluation.eval_set.EvalSet` etc.) can generate valid
  evalset JSON programmatically.

**Lessons from a real failure** (divide_by_zero case): trajectory scored 1.0 every run,
but response_match was 0.32 then 0.71 across runs — (1) golden responses must be
*recorded from a validated run*, not hand-authored; (2) even then, LLM phrasing varies
per run, so keep response thresholds tolerant (~0.5–0.7) and let trajectory=1.0 be the
hard gate. CI integration: run `uv run adk eval` in GitHub Actions to catch regressions.

## Module 25 — observability: plugins + OpenTelemetry (`observability_agent/`)

**Plugins** are cross-cutting lifecycle hooks attached to the **App** (not the Agent):
subclass `BasePlugin` and override any of ~14 callbacks — `before/after_run`,
`before/after_agent`, `before/after_model`, `before/after_tool`, `on_event`,
`on_user_message`, and the error trio `on_model/tool/agent_error_callback`.

- Lab: `AlertingPlugin` counts consecutive model errors via `on_model_error_callback`
  (returning `None` re-raises; returning an `LlmResponse` would swallow the error —
  fallback pattern), resets on `after_model_callback`, escalates at a threshold.
  Verified live + simulated: 3-error streak fired the critical alert; success reset to 0.
- Enterprise telemetry: `get_gcp_exporters(enable_cloud_tracing=True, ...)` +
  `maybe_set_otel_providers(...)` ship traces/metrics to Cloud Trace/Monitoring
  (needs GCP creds — gated behind `ENABLE_GCP_TELEMETRY=1` in our repo).
- **ADK 2.7 fix vs handout:** `event.event_type` does not exist — use the dedicated
  callbacks instead of string-matching event types.

## Module 25.5 — RAI safety plugins (`safety_guard/`)

"Instructions are just advice" applied to safety: a plugin is a **deterministic layer
outside the LLM's reasoning** — regex cannot be prompt-injected.

- `PIIGuardrailPlugin.on_event_callback` inspects every event before it is persisted and
  yielded; returning a modified `Event` replaces it (**fail-closed**: whole response
  withheld, not redacted).
- Verified live: a cooperative `leak_agent` asked to repeat a credit-card number — the
  user saw only `[SECURITY BLOCK] ...`; harmless messages passed untouched.
- Extensions: competitor-name redaction, secondary safety-model scoring, URL whitelists.
- Placement matters: `on_user_message_callback` filters inbound, `before_model_callback`
  guards prompts, `on_event_callback` is the last gate before the user sees anything.

## Module 26 — callbacks & guardrails (`content_moderator/`)

Same hooks as module 25's plugins, but **agent-level**: passed as constructor args to one
`Agent`. Rule of thumb: plugin = fleet policy (whole App), callback = this agent's own
behavior. The short-circuit contract:

| Callback | Return `None` | Return a value |
|---|---|---|
| `before_agent` | proceed | `types.Content` ⇒ skip the whole turn (cache hit) |
| `before_model` | proceed | `LlmResponse` ⇒ skip the LLM call (input guardrail) |
| `after_model` | keep response | `LlmResponse` ⇒ replace it (output filter/redaction) |
| `before_tool` | run tool | `dict` ⇒ skip tool, use dict as its result (arg validation) |
| `after_agent` | — | observe only (cache save) |

Verified live, with two honest findings:

- Blocked-word prompt answered by the canned refusal with **zero LLM calls**; email
  redacted to `[EMAIL_REDACTED]`; cache-hit replayed the previous answer skipping
  everything.
- **The model pre-empted the tool guardrail**: asked for `word_count=10000`, it read the
  docstring ("max 5000") and called with 5000 itself — the validation callback never
  fired. Good docstrings prevent violations; the callback stays as the backstop for when
  the model doesn't comply. Defense in depth, not either/or.
- **The lab's cache is deliberately naive** — it replays the last answer for ANY next
  message (asked "capital of France?", got `[CACHED]: 4`). Real caching must key on the
  normalized query; the lab only teaches the short-circuit mechanism.
- Watch-out: a short-circuited refusal also got cache-saved — callbacks compose, and
  side effects of one hook feed the next. Order your hooks' assumptions carefully.

## Module 27 — intro to MCP (`mcp_agent/`)

MCP (Model Context Protocol) = module 14's adapter idea at **protocol level**: any MCP
server plugs into ADK without a per-tool Python adapter. `MCPToolset` connects, discovers
the server's tools dynamically, and adapts them all.

```python
MCPToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", SANDBOX_DIR]),
        timeout=60.0),          # default 5s dies on first npx download
    tool_filter=["list_directory", "read_file"])
```

Two independent security layers, both verified live:
- **Sandbox**: the directory passed to the server is a hard filesystem boundary.
- **`tool_filter`**: the server exposes write/delete tools too, but the LLM never sees
  them — a delete request produced *zero* tool calls and a polite refusal.

Setup gotchas (ADK 2.7): needs Node.js (server runs via `npx` as a stdio subprocess) and
`uv add "mcp<2"` — mcp 2.0 broke the imports ADK expects (`mcp.shared.session`). The
default 5s session timeout fails on the first run while npx downloads the package.

## Module 28 — building a custom MCP server (`custom_mcp_server/`)

The provider side: a stateful shopping-cart server in ~90 lines with the low-level MCP
SDK, consumed by an ADK agent with the exact same `MCPToolset` pattern as module 27.

Server anatomy (`cart_server.py`):
- `Server("shopping-cart")` + two decorated handlers: `@app.list_tools()` returns `Tool`
  objects (name, description, JSON `inputSchema` — the MCP equivalent of module 9's
  docstring/type-hint lesson), `@app.call_tool()` dispatches by name and returns
  `[TextContent(text=json.dumps(result))]`.
- Transport: `mcp.server.stdio.stdio_server()` — the client spawns us as a subprocess.
- State: module-level dict → lives per server process. The toolset keeps one subprocess
  per session alive, so cart state survived across turns; it dies with the process
  (production: Redis/Firestore behind the handlers).

Consumer notes: `command=sys.executable` so the subprocess uses the venv's Python.
Verified live: parallel adds in one turn (milk + bread), another add next turn, view_cart
returned all three — cross-turn state in the server confirmed.

Why it matters: the server is agent-framework-agnostic — the same file plugs into Claude
Desktop, IDEs, or any MCP client unchanged. Tool logic becomes a reusable service, not
agent code.

## Module 29 — UI integration: custom SSE chat (`ui_agent/`)

A self-contained `index.html` chatting with the api_server — no dev UI involved.
The repo folder is the **API provider** (agents over HTTP), the custom page is the
**SSE chat client**. Two terminals, two lines:

```sh
uv run adk api_server --allow_origins http://localhost:8081 --allow_origins null .
python -m http.server 8081 -d ui_agent    # then open http://localhost:8081
```

- CORS is mandatory for a browser page on another origin; don't pass `*` — uv/shell
  glob-expands it into your folder names.
- Flow (verified headless): 1) `POST /apps/{app}/users/{u}/sessions/{sid}` (must exist
  first), 2) `POST /run_sse` with `{"app_name", "user_id", "session_id", "new_message",
  "streaming": true}`, 3) read the body as a stream, parse `data: {json}` lines, append
  `content.parts[0].text` — `partial: true` events carry increments.
- Session persistence across page reloads: keep the session id in `localStorage`
  (regenerating per load loses the conversation — the lab's self-reflection point).

## Module 30 — custom live streaming client (`streaming_agent/` + `custom_streaming_app/`)

Bidirectional WebSocket streaming — the transport behind voice agents. Same two-terminal
shape as module 29 (folder = API provider, page = client):

```sh
uv run adk api_server --allow_origins http://localhost:8081 --allow_origins null .
python -m http.server 8081 -d custom_streaming_app    # then open http://localhost:8081
```

In the page: **Connect** (creates the session, opens the WebSocket), type a message or
**Start Mic**, watch audio chunks arrive in the transcript.

`streaming_agent` is live-only: its model rejects normal chat (`generateContent` 404) —
use it exclusively through this client, never the dev UI chat box.

- **Real ADK 2.7 endpoint** (lab handout's `/live/{id}` is outdated):
  `ws://host:8000/run_live?app_name=..&user_id=..&session_id=..&modalities=AUDIO`
  — session must exist first, same as SSE.
- Client → server messages are `LiveRequest` JSON: `{"content": {...}}` for text,
  `{"blob": {mimeType, data(base64)}}` for mic audio chunks; server → client messages
  are event JSON (text parts and/or `inlineData` audio).
- **Model requirement**: `bidiGenerateContent` support. Regular flash models are rejected
  (`gemini-3.6-flash` failed); live models may also reject TEXT response modality —
  `gemini-3.1-flash-live-preview` answers in AUDIO only.
- Verified headless: text question over the socket → 9 audio chunks (~91 KiB) streamed
  back. Browser playback of the PCM chunks (Web Audio API) left as the extension.

SSE (29) vs WebSocket (30): SSE = server→client streaming over plain HTTP, perfect for
chat text; WebSocket = full duplex, required when the *client* also streams (voice).
