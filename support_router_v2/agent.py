"""Module 18 - dynamic orchestration: programmable graphs with @node.

Instead of declaring edges, an orchestrator function drives sub-nodes with
plain Python: `await ctx.run_node(some_agent, input)` executes an agent and
returns its result directly. if/else, loops, retries - any control flow
Python can express, the workflow can run.

    START ─> support_router_workflow
                ├─ ctx.run_node(classifier)        (always)
                └─ ctx.run_node(human_escalation)  if angry
                   ctx.run_node(ai_support)        otherwise
"""

from typing import Literal

from pydantic import BaseModel

from google.adk import Agent, Workflow
from google.adk.agents.context import Context
from google.adk.workflow import node

ai_support = Agent(
    name="ai_support_bot",
    model="gemini-3.6-flash",
    instruction="You are a helpful customer support AI. Answer technical questions clearly.",
)

human_escalation = Agent(
    name="human_escalation_team",
    model="gemini-3.6-flash",
    instruction=(
        "You are a human support representative talking to a frustrated customer. "
        "Apologize sincerely and promise a phone call from a senior agent."
    ),
)


class SentimentClassification(BaseModel):
    sentiment: Literal["angry", "neutral", "happy"]


classifier = Agent(
    name="classifier",
    model="gemini-3.6-flash",
    instruction="Classify the sentiment of the user's latest message.",
    output_schema=SentimentClassification,
)


@node(rerun_on_resume=True)
async def support_router_workflow(ctx: Context, node_input: str):
    """Orchestrates classification and routing in plain Python."""
    # run_node returns the structured output as a plain dict - validate it
    # back into the schema for typed access.
    result = await ctx.run_node(classifier, node_input)
    classification = SentimentClassification.model_validate(result)

    if classification.sentiment == "angry":
        chosen_agent = human_escalation
    else:
        chosen_agent = ai_support

    return await ctx.run_node(chosen_agent, node_input)


root_agent = Workflow(
    name="SupportSystem",
    edges=[("START", support_router_workflow)],
)
