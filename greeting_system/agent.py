"""Module 15 - multi-agent greeting system: router + specialist.

Delegation mechanics: the router's LLM sees its sub_agents (name +
description) and can emit a transfer_to_agent action; ADK then hands the
conversation to the specialist, which answers the user directly.
"""

from google.adk import Agent, Workflow

from . import spanish_greeter_agent

router = Agent(
    name="router_agent",
    model="gemini-3.6-flash",
    instruction="""You are a language routing specialist. Your primary function is to
identify the language requested by the user and delegate the task to the correct
sub-node. Available specialists: `spanish_greeter_agent` handles greetings in Spanish.
Rules:
1. If the user requests a Spanish greeting, transfer to `spanish_greeter_agent`.
2. If the language is unsupported, politely inform the user you don't have a
   specialist for that language yet.""",
    sub_agents=[spanish_greeter_agent.agent],
)

root_agent = Workflow(
    name="GreetingSystem",
    edges=[("START", router)],
)
