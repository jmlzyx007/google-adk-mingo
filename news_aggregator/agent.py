"""Module 16 - static orchestration: parallel fan-out, join, then summarize.

The graph is fixed at build time (no LLM routing decisions):

    START ─┬─> tech_researcher ──┐
           │                     ├─> news_sync (JoinNode) ─> summarizer
           └─> market_researcher ┘

Both researchers run concurrently; the JoinNode waits for both branches;
the summarizer reads their results from state via {tech_news}/{market_news}
placeholders (written by output_key).
"""

from google.adk import Agent, Workflow
from google.adk.workflow import JoinNode

tech_researcher = Agent(
    name="tech_researcher",
    model="gemini-3.6-flash",
    instruction="Find 3 exciting headlines about AI and Robotics. Be concise.",
    output_key="tech_news",
)

market_researcher = Agent(
    name="market_researcher",
    model="gemini-3.6-flash",
    instruction="Find 3 key headlines about Stock Market trends. Be concise.",
    output_key="market_news",
)

summarizer = Agent(
    name="summarizer",
    model="gemini-3.6-flash",
    instruction="""
    You are a news editor. Create a brief newsletter using the data provided:
    TECH: {tech_news}
    MARKET: {market_news}

    Synthesize the information into a single, cohesive daily briefing.
    """,
)

syncer = JoinNode(name="news_sync")

root_agent = Workflow(
    name="NewsSystem",
    edges=[
        ("START", tech_researcher, syncer),
        ("START", market_researcher, syncer),
        (syncer, summarizer),
    ],
)
