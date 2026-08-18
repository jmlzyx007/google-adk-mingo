"""Module 10 - memory agent using stateful custom tools."""

from google.adk import Agent

from .tools.memory import store_name, recall_name

root_agent = Agent(
    name="memory_agent",
    model="gemini-3.6-flash",
    description="An agent that remembers users.",
    instruction="""You are a friendly assistant.
    Use 'store_name' if the user introduces themselves.
    Use 'recall_name' if they ask for their name.""",
    tools=[store_name, recall_name],
)
