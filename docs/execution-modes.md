# The 3 execution modes (module 5)

ADK agents can be executed in three ways, all from the repo root.

## 1. Web UI mode — interactive development

```sh
uv run adk web .
```

Launches the dev UI at `http://127.0.0.1:8080`, discovering every agent folder (dropdown selection). Best for debugging: the **Trace** tab shows a waterfall of every step and the full prompts sent to the model, and the **State** tab shows session state (e.g. `output_key` values).

Multimodal agents can be tested here too: use the attachment icon next to the message box to upload an image alongside your text.

## 2. Command-line mode — headless interaction

```sh
uv run adk run echo_agent
```

Direct conversation with one agent in the terminal (`[user]:` prompt). Good for quick tests and scripting. Exit with `Ctrl+C`.

## 3. API server mode — long-running HTTP service

```sh
uv run adk api_server
```

Serves the agents over HTTP at `http://127.0.0.1:8000`. A session must be created explicitly before messaging:

```sh
# 1. Create a session
curl -X POST http://127.0.0.1:8000/apps/support_analyzer/users/u1/sessions/s1

# 2. Send a message (streamed JSON events; the answer is in event.name == 'agent:response')
curl -X POST http://127.0.0.1:8000/run_sse \
  -H "Content-Type: application/json" \
  -d '{"app_name": "support_analyzer", "user_id": "u1", "session_id": "s1", "new_message": {"role": "user", "parts": [{"text": "My invoice is wrong"}]}}'
```

## How discovery works

`adk web` / `adk run` find agents by scanning subfolders of the agents directory: any
folder that imports as a Python package and exposes a module-level **`root_agent`**
(convention: `__init__.py` does `from . import agent`, `agent.py` defines `root_agent`)
appears in the UI under the folder's name. Hidden folders (`.adk/`, `.venv/`) are skipped.

Standalone scripts (module 6/7 style, building `App` + `InMemoryRunner` themselves) don't
need this convention — run them with `uv run python <folder>/main.py`. Defining the agent
in `agent.py` and importing it from `main.py` makes the same agent work both ways.
