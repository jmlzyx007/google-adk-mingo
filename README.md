# google-adk-mingo

My working repo for the [Google ADK Training: From Zero to Hero](https://mauripsale.github.io/doc-adk-training/) course — building AI agents with the **Google Agent Development Kit (ADK) v2.0**.

## Setup

Requirements: Python 3.11+, [uv](https://docs.astral.sh/uv/), a Google API key ([AI Studio](https://aistudio.google.com/apikey)) or a GCP project.

```sh
uv sync
copy .env.example .env   # then paste your GOOGLE_API_KEY into .env
```

## Run

Launch the ADK dev UI from the repo root — it discovers every agent folder:

```sh
uv run adk web .
```

Or chat with a specific agent in the terminal:

```sh
uv run adk run echo_agent
```

## Course progress

7 parts, 40 modules. Each lab gets its own agent folder in this repo.

- [x] Part 1 — Foundations (modules 1–7): `echo_agent/` (module 3)
- [ ] Part 2 — Tools & Capabilities (modules 8–14)
- [ ] Part 3 — Multi-Agent Systems (modules 15–21)
- [ ] Part 4 — Production Readiness (modules 22–26)
- [ ] Part 5 — Advanced Integrations, MCP & UI (modules 27–30)
- [ ] Part 6 — Deployment & Enterprise (modules 31–36)
- [ ] Part 7 — Capstone & Best Practices (modules 37–40)

## Layout

```
echo_agent/          # one folder per agent lab
  __init__.py        #   exposes `agent` so ADK can discover it
  agent.py           #   defines `root_agent`
.env.example         # auth template (copy to .env — never committed)
pyproject.toml       # uv project, google-adk >= 2.7
```
