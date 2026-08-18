from google.adk import Agent
from google.adk.tools import google_search

root_agent = Agent(
    name="researcher_agent",
    model="gemini-3.6-flash",
    description="An agent that can research current events using Google Search.",
    instruction=(
        "You are a helpful research assistant. "
        "Your job is to answer the user's questions accurately. "
        "If the question is about a recent event, a specific person, or anything that might require up-to-date information, you MUST use the `google_search` tool. "
        "Do not rely on your own knowledge for topics that could have changed since your training."
    ),
    tools=[
        google_search
    ],
)