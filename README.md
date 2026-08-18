# google-adk-mingo

My working repo for the [Google ADK Training: From Zero to Hero](https://mauripsale.github.io/doc-adk-training/) course — building AI agents with the **Google Agent Development Kit (ADK) v2.0**.

## Quick start

```sh
uv sync
copy .env.example .env   # paste your GOOGLE_API_KEY into .env
uv run adk web .         # dev UI at http://127.0.0.1:8080
```

Full details: [docs/setup.md](docs/setup.md) · [docs/execution-modes.md](docs/execution-modes.md)

## Course progress

7 parts, 40 modules. Each lab gets its own agent folder in this repo.

- [x] **Part 1 — Foundations (modules 1–7): done** — `echo_agent/` (module 3), `support_analyzer/` (modules 4–6), `visual_catalog/` (module 7)
- [x] **Part 2 — Tools & Capabilities (modules 8–14): done** — `researcher_agent/` (8), `calculator_agent/` (9), `memory_agent/` (10), `market_analyst/` (11), `research_assistant/` (12), `secure_finance/` (13), `persistent_agent/` (13.5), `fact_finder_agent/` (14)
- [x] **Part 3 — Multi-Agent Systems (modules 15–21): done** — `greeting_system/` (15), `news_aggregator/` (16), `market_router/` (17), `support_router_v2/` (18), `travel_team/` (19), `essay_refiner/` (20), `research_specialist/` + `a2a_orchestrator/` (21)
- [ ] Part 4 — Production Readiness (modules 22–26)
- [ ] Part 5 — Advanced Integrations, MCP & UI (modules 27–30)
- [ ] Part 6 — Deployment & Enterprise (modules 31–36)
- [ ] Part 7 — Capstone & Best Practices (modules 37–40)

## Docs

- [Setup](docs/setup.md) — uv workflow, auth options, environment checks, model-name gotcha
- [Execution modes](docs/execution-modes.md) — web UI vs CLI vs API server, agent discovery
- [Module notes](docs/module-notes.md) — lessons per module (structured output, model switching, logging, multimodal, tools, persistence)
- [LangChain ecosystem](docs/langchain-ecosystem.md) — what the module 14 adapter unlocks, package landscape, caveats

## Layout

```
echo_agent/          # module 3 — first agent (discovery convention)
support_analyzer/    # modules 4-6 — structured output, model switching, programmatic runs
visual_catalog/      # module 7 — multimodal (agent.py + standalone main.py)
researcher_agent/    # module 8 — built-in google_search tool
calculator_agent/    # module 9 — custom function tools
memory_agent/        # module 10 — stateful tools (ToolContext.state)
market_analyst/      # module 11 — OpenAPI toolset (Frankfurter API)
research_assistant/  # module 12 — grounding + custom tools mixed
secure_finance/      # module 13 — HITL confirmation, actions, Workflow graph
persistent_agent/    # module 13.5 — custom Firestore session service (needs GCP)
fact_finder_agent/   # module 14 — LangChain Wikipedia tool via adapter
greeting_system/     # module 15 — router + specialist (sub_agents transfer)
news_aggregator/     # module 16 — static orchestration (parallel edges + JoinNode)
market_router/       # module 17 — structured routing (Literal schema + dict edges)
support_router_v2/   # module 18 — dynamic orchestration (@node + ctx.run_node)
travel_team/         # module 19 — collaborative team (modes: single_turn / task)
essay_refiner/       # module 20 — cyclic workflow (critique/refine loop + hard cap)
research_specialist/ # module 21 — A2A remote specialist (uvicorn server, port 8001)
a2a_orchestrator/    # module 21 — A2A client (RemoteA2aAgent as sub-agent)
docs/                # split-out documentation
verify_setup.py      # quick environment smoke test
.env.example         # auth template (copy to .env — never committed)
pyproject.toml       # uv project, google-adk >= 2.7
```

Each agent folder follows the ADK convention: `__init__.py` exposes `agent`, `agent.py` defines `root_agent`.
