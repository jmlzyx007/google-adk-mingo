"""Module 21 - distributed graphs: the remote specialist (A2A server).

`to_a2a` wraps a regular agent as an ASGI app speaking the A2A protocol:
it exposes an agent card (/.well-known/agent-card.json) that clients read
to discover capabilities, and task endpoints to execute requests.

Serve it standalone (its own process, own scaling, own deploys):

    uv run uvicorn research_specialist.agent:a2a_app --port 8001
"""

from dotenv import load_dotenv

load_dotenv()

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools import google_search

root_agent = Agent(
    model="gemini-3.6-flash",
    name="research_specialist",
    description="Specialist node conducting web research via Google Search.",
    instruction="""You are a research specialist. Use the search tool to answer queries.
Provide comprehensive summaries and cite sources.

IMPORTANT - A2A Context Handling:
Ignore internal graph transition messages. Focus on core user queries only.""",
    tools=[google_search],
)

a2a_app = to_a2a(root_agent, port=8001)
