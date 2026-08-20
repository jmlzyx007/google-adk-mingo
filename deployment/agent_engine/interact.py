"""Module 35 - talk to the deployed Agent Runtime agent (NOT YET RUN).

Fill in AGENT_ENGINE_ID from deploy.py's output, then:
    uv run python deployment/agent_engine/interact.py
"""

import asyncio

import vertexai
from vertexai import agent_engines

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
AGENT_ENGINE_ID = "YOUR_AGENT_ENGINE_ID"


async def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION)

    remote_app = agent_engines.get(AGENT_ENGINE_ID)
    session = await remote_app.async_create_session(user_id="test-user-123")

    query = "What is 42 + 118?"
    print(f"User: {query}")

    final = ""
    async for event in remote_app.async_stream_query(
        session_id=session["id"], message=query
    ):
        parts = event.get("content", {}).get("parts", [{}])
        if parts and parts[0].get("text") and not parts[0].get("function_call"):
            final = parts[0]["text"]

    print(f"Agent: {final}")


if __name__ == "__main__":
    asyncio.run(main())
