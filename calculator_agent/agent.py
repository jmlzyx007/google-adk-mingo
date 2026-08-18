"""Module 9 - calculator agent using custom function tools."""

from google.adk import Agent

from .tools.calculator import add, subtract, multiply, divide

root_agent = Agent(
    name="calculator_agent",
    model="gemini-3.6-flash",
    description="An agent that performs arithmetic calculations.",
    instruction="""You are a helpful calculator assistant. When asked to calculate,
use the appropriate tool. State results clearly. Politely decline non-math requests.""",
    tools=[add, subtract, multiply, divide],
)
