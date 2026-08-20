"""Module 29 - UI integration: the agent behind a custom chat frontend.

Nothing UI-specific here - any agent works. The integration story lives in
index.html (SSE client) and in how the api_server is launched:

    uv run adk api_server --allow_origins "*"   # CORS for the browser page
"""

from google.adk import Agent

root_agent = Agent(
    name="ui_agent",
    model="gemini-3.6-flash",
    description="Friendly assistant behind the custom chat UI.",
    instruction=(
        "You are a friendly, concise assistant. Answer the user's questions "
        "in short paragraphs suitable for a chat window."
    ),
)
