"""Module 13 - secure finance agent: HITL confirmation + runtime escalation."""

from google.adk import Agent, Workflow
from google.adk.tools import FunctionTool

from .tools.finance import execute_investment

# Supervisor sub-agent for high-value requests
supervisor = Agent(
    name="supervisor",
    model="gemini-3.6-flash",
    instruction="""You are a senior investment supervisor reviewing
    large investments (>$10,000). Provide professional recommendations.""",
)

# Human-in-the-loop gate: ADK will not call the function until the user
# explicitly approves the tool call - a framework guarantee, not a prompt.
secure_investment_tool = FunctionTool(
    execute_investment,
    require_confirmation=True,
)

finance_agent = Agent(
    name="finance_agent",
    model="gemini-3.6-flash",
    description="Secure finance assistant",
    instruction="""Help users with investments using execute_investment.
    Amounts exceeding $10k escalate to supervisor.""",
    tools=[secure_investment_tool],
    sub_agents=[supervisor],
)

# Workflow graph starting at finance_agent
root_agent = Workflow(
    name="SecureSystem",
    edges=[("START", finance_agent)],
)
