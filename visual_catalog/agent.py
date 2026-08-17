"""Module 7 - multimodal catalog writer agent.

Defined here (discovery convention) so it works both in `adk web`
and programmatically via main.py.
"""

from google.adk import Agent

root_agent = Agent(
    model='gemini-3.6-flash',
    name='catalog_writer',
    instruction="""
        You are an expert product catalog writer.
        Your task is to analyze the provided image and generate a compelling,
        professional description for a web catalog.
        Highlight the main features, materials, and potential use cases.
    """.strip()
)
