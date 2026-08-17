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
- [ ] Part 2 — Tools & Capabilities (modules 8–14)
- [ ] Part 3 — Multi-Agent Systems (modules 15–21)
- [ ] Part 4 — Production Readiness (modules 22–26)
- [ ] Part 5 — Advanced Integrations, MCP & UI (modules 27–30)
- [ ] Part 6 — Deployment & Enterprise (modules 31–36)
- [ ] Part 7 — Capstone & Best Practices (modules 37–40)

## Docs

- [Setup](docs/setup.md) — uv workflow, auth options, environment checks, model-name gotcha
- [Execution modes](docs/execution-modes.md) — web UI vs CLI vs API server, agent discovery
- [Module notes](docs/module-notes.md) — lessons per module (structured output, model switching, logging, multimodal)

## Layout

```
echo_agent/          # module 3 — first agent (discovery convention)
support_analyzer/    # modules 4-6 — structured output, model switching, programmatic runs
visual_catalog/      # module 7 — multimodal (agent.py + standalone main.py)
docs/                # split-out documentation
verify_setup.py      # quick environment smoke test
.env.example         # auth template (copy to .env — never committed)
pyproject.toml       # uv project, google-adk >= 2.7
```

Each agent folder follows the ADK convention: `__init__.py` exposes `agent`, `agent.py` defines `root_agent`.
