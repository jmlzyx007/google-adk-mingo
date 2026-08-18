"""Module 21 - distributed graphs: the orchestrator (A2A client).

`RemoteA2aAgent` makes an agent running in ANOTHER PROCESS (or another
machine / Cloud Run service) look like a local sub-agent: the coordinator
delegates to it exactly as it would to an in-process specialist. The
network layer is fully abstracted behind the agent card.

Requires the specialist to be running first:

    uv run uvicorn research_specialist.agent:a2a_app --port 8001
"""

from dotenv import load_dotenv

load_dotenv()

from google.adk import Agent, Workflow
from google.adk.agents.remote_a2a_agent import (
    AGENT_CARD_WELL_KNOWN_PATH,
    RemoteA2aAgent,
)

remote_researcher = RemoteA2aAgent(
    name="remote_researcher",
    description="Remote specialist for web research.",
    agent_card=f"http://localhost:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)

coordinator = Agent(
    model="gemini-3.6-flash",
    name="coordinator",
    # Dispatching parent of dynamically scheduled sub-agents (module 19 lesson).
    rerun_on_resume=True,
    instruction="Analyze requests. Delegate research questions to 'remote_researcher'.",
    sub_agents=[remote_researcher],
)

root_agent = Workflow(
    name="DistributedSupportSystem",
    edges=[("START", coordinator)],
)
