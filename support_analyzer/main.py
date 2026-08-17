import asyncio
from dotenv import load_dotenv
from google.adk.apps import App
from google.adk.runners import InMemoryRunner
from agent import root_agent

load_dotenv()

# 1. Create the App container.
# This separates infrastructure (App) from intelligence (Agent).
# In ADK 2.0, root_agent is passed as a named argument.
app = App(name="support_app", root_agent=root_agent)

# 2. Initialize the Runner.
# We pass the 'app' instance to the Runner.
runner = InMemoryRunner(app=app)

async def main():
    print("--- User A (Alice) ---")
    # 3. Run for Alice (Billing Issue)
    # run_debug automatically prints the agent response to the terminal.
    events_a = await runner.run_debug("I was overcharged $50.", user_id="Alice")
    
    # Optional: If you need to access the text in code, iterate through events:
    for event in events_a:
        if event.is_final_response():
            print(f"DEBUG: Alice's JSON: {event.content.parts[0].text}")

    print("\n--- User B (Bob) ---")
    # 4. Run for Bob (Technical Issue)
    # Even with the same Runner, Bob's state is separate from Alice's.
    await runner.run_debug("My wifi is not working.", user_id="Bob")

if __name__ == "__main__":
    asyncio.run(main())