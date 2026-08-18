# LangChain ecosystem exploration (module 14 follow-up)

Why ADK ships a `LangchainTool` adapter, and what it unlocks.

## What LangChain is — two separable things

1. **An orchestration framework** — chains, agents, prompt templates, memory abstractions.
   Competes with ADK; we don't use it (ADK is our orchestrator).
2. **The largest integration catalog in the LLM space** — hundreds of connectors to external
   services, each wrapped in a standard `BaseTool` interface. *This* is what
   `LangchainTool` gives access to: Google adapts the catalog instead of rewriting it.

## Package landscape

| Package | Role |
|---|---|
| `langchain-core` | Base interfaces (`BaseTool`, runnables, messages) — tiny, everything depends on it |
| `langchain-community` | The big grab-bag of community-maintained integrations (our `WikipediaQueryRun` lives here) |
| `langchain-openai`, `langchain-google-genai`, … | Model-provider bindings — irrelevant for us, ADK talks to Gemini natively |
| LangGraph | Their graph-based agent orchestrator (ADK `Workflow`'s direct competitor) |
| LangSmith | Observability/tracing SaaS (ADK counterpart: Trace tab + OpenTelemetry) |

## Tool catalog highlights (all adaptable with one line)

- **Search**: Tavily, DuckDuckGo, Brave, SerpAPI — useful since `google_search` is a
  built-in with mixing constraints on older models
- **Knowledge**: Wikipedia, ArXiv, PubMed, Wolfram Alpha, Wikidata
- **Data**: SQL databases, Pandas dataframes, GraphQL endpoints
- **Web**: HTTP request wrappers, Playwright browser toolkits, YouTube transcripts
- **Workplace**: Gmail, Slack, Jira, GitHub, Office365 toolkits
- **Files**: filesystem read/write toolkits

The pattern is always the same as `fact_finder_agent/agent.py`: instantiate the LangChain
tool (often with a config wrapper, e.g. `WikipediaAPIWrapper(top_k_results=1, ...)`), then
wrap it: `LangchainTool(tool=...)`.

## Caveats

- **Quality varies** — `langchain-community` is community-maintained; some tools are
  polished, some abandoned. Vet before relying on one.
- **Own credentials & extra packages** — many tools need their own API key (Tavily, Slack…)
  and a pip dependency (we added `wikipedia` alongside `langchain-community`).
- **Schemas were written for LangChain agents** — if the ADK agent misuses an adapted tool,
  tighten your agent `instruction` (same module 9 lesson: the description drives tool use).
- **Only import the tool half** — reaching for LangChain chains/memory/agents inside an ADK
  project means two frameworks fighting over the same job. Adapter for tools, ADK for
  everything else.

ADK ships a sibling adapter for **CrewAI** tools (`CrewaiTool`) — same idea, smaller
catalog. Strategic takeaway: ADK bets that agent frameworks win on *interoperability*; its
tool layer absorbs other ecosystems rather than competing with them.
