"""Module 15 - specialist sub-agent.

The `description` is what the router's LLM reads when deciding whether to
transfer here - it is the agent's advertisement to its parent.
"""

from google.adk import Agent

agent = Agent(
    name="spanish_greeter_agent",
    model="gemini-3.6-flash",
    description="Expert at providing warm greetings in Spanish.",
    instruction="""You are a friendly assistant who communicates ONLY in Spanish.
Provide a single, warm greeting and then stop.""",
)
