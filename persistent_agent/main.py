"""Module 13.5 - run the persistent agent against Firestore.

Usage (from the repo root, message as argument):

    uv run python persistent_agent/main.py "My favorite color is blue."
    # stop the process, then run again:
    uv run python persistent_agent/main.py "What is my favorite color?"

Requires GOOGLE_CLOUD_PROJECT in .env, Firestore enabled (Native mode),
and gcloud Application Default Credentials.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from google.adk import Runner
from google.adk.apps import App
from google.genai import types

from agent import root_agent
from firestore_provider import FirestoreSessionService

load_dotenv()

USER_ID = "student_1"
SESSION_ID = "persistent_demo"


async def main():
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        sys.exit("Set GOOGLE_CLOUD_PROJECT in .env to use Firestore persistence.")

    message = sys.argv[1] if len(sys.argv) > 1 else "What is my favorite color?"

    app = App(name="extensibility_demo", root_agent=root_agent)
    session_service = FirestoreSessionService(project_id=project_id)
    runner = Runner(app=app, session_service=session_service)

    # Reuse the stored session if it exists - this is what makes the memory
    # survive restarts. Only create it on the very first run.
    session = await session_service.get_session(
        app_name=app.name, user_id=USER_ID, session_id=SESSION_ID
    )
    if session is None:
        print("(no stored session found - creating a fresh one)")
        await session_service.create_session(
            app_name=app.name, user_id=USER_ID, session_id=SESSION_ID
        )
    else:
        print(f"(resumed session with {len(session.events)} stored events)")

    msg = types.Content(role="user", parts=[types.Part(text=message)])
    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=msg
    ):
        if event.is_final_response():
            print("agent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
