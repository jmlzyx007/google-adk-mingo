"""Module 19 - collaborative teams: modes control the hand-off contract.

Unlike module 15 (where the specialist kept the conversation after a
transfer), a `mode` makes the return-to-parent deterministic:

- mode="single_turn": answer once, control returns to the parent. No user
  interaction - right for pure data retrieval.
- mode="task": may interact with the user (clarifying questions) until its
  objective completes, then control returns to the parent.
- coordinator (no mode): owns the conversation, delegates, synthesizes.
"""

from google.adk import Agent

weather_agent = Agent(
    name="weather_checker",
    model="gemini-3.6-flash",
    mode="single_turn",
    instruction="Provide a brief, enthusiastic 3-day weather forecast for the user's destination.",
)

flight_agent = Agent(
    name="flight_booker",
    model="gemini-3.6-flash",
    mode="task",
    instruction="""
    Help the user book a flight.
    1. Ask for their preferred airline or time if not provided.
    2. Once you have the info, confirm the 'booking' (simulated) and stop.
    """,
)

root_agent = Agent(
    name="travel_planner",
    model="gemini-3.6-flash",
    # A node that dynamically dispatches sub-agents (task/single_turn modes)
    # must be resumable: if a child is interrupted, the parent re-runs on
    # wake-up to collect the child's response.
    rerun_on_resume=True,
    instruction="""
    You are a travel planning coordinator.
    Your goal is to build a complete plan for the user.

    PROCESS:
    1. Call the `weather_checker` to get the forecast.
    2. Call the `flight_booker` to arrange travel.
    3. Once both sub-tasks are done, present a final summary to the user.
    """,
    sub_agents=[weather_agent, flight_agent],
)
