"""Module 13.5 - agent whose memory survives process restarts."""

from google.adk import Agent

root_agent = Agent(
    name="persistent_agent",
    model="gemini-3.6-flash",
    description="An assistant that remembers the user across process restarts.",
    instruction=(
        "You are a helpful assistant that remembers what the user tells you, "
        "such as their favorite color. Answer questions about previously "
        "shared facts using the conversation history."
    ),
)
