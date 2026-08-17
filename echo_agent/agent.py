"""Module 3 — First agent: a simple echo agent."""

from google.adk.agents import Agent

root_agent = Agent(
    name="echo_agent",
    model="gemini-3.6-flash",
    description="A simple agent that echoes back what the user says.",
    instruction=(
        "You are an echo agent. Repeat back exactly what the user says, "
        "prefixed with 'Echo: '. Do not add anything else."
    ),
)
