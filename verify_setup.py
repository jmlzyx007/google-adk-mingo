# verify_setup.py
import asyncio
import os
from dotenv import load_dotenv
from google.adk import Agent
from google.adk.apps import App
from google.adk.runners import InMemoryRunner

async def main():
    load_dotenv()
    
    print("Testing ADK 2.0 Environment...")

    try:
        # 1. Define a simple Node (Agent)
        agent = Agent(
            name="verify_agent",
            model="gemini-3.6-flash",
            instruction="Respond with: 'ADK 2.0 is Ready!'"
        )

        # 2. Create the App
        app = App(name="verify_app", root_agent=agent)

        # 3. Initialize the Runner
        runner = InMemoryRunner(app=app)

        # 4. Execute using the new run_debug helper
        print("Connecting to LLM...")
        events = await runner.run_debug("Hello!", user_id="test_user")
        
        # Verify the response
        ready = False
        for event in events:
            if event.is_final_response():
                print(f"Agent Response: {event.content.parts[0].text}")
                ready = True
        
        if ready:
            print("\nSETUP COMPLETE! You are running ADK 2.0.")
        else:
            print("\nFailed to get a final response from the agent.")

    except ImportError as e:
        print(f"Version Error: {e}")
        print("Ensure you installed google-adk>=2.1.0")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())

