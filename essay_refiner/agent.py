"""Module 20 - cyclic workflows: iteration and self-correction.

A write -> critique -> refine cycle that repeats until the critic approves,
with a hard iteration cap. LLMs are non-deterministic: without the cap, a
never-satisfied critic means an infinite loop and runaway API costs. The
`for` loop is the guaranteed stop; "APPROVED" is the happy exit.

    writer ─> critic ─(APPROVED)─> done
                 └─(feedback)─> refiner ─> critic ─> ... (max 3 rounds)
"""

from google.adk import Agent, Workflow
from google.adk.agents.context import Context
from google.adk.workflow import node

writer = Agent(
    name="writer",
    model="gemini-3.6-flash",
    instruction="Write a 2-sentence story about the topic the user gives you. Output only the story.",
)

critic = Agent(
    name="critic",
    model="gemini-3.6-flash",
    instruction=(
        "You are a very strict literary critic. Evaluate the story you are given. "
        "On a first submission, always find something concrete to improve and respond "
        "with one short sentence of feedback. Only respond with the single word "
        "APPROVED if the story is vivid, coherent, exactly 2 sentences, and you "
        "genuinely cannot suggest any improvement."
    ),
)

refiner = Agent(
    name="refiner",
    model="gemini-3.6-flash",
    instruction=(
        "You improve stories. You are given a story and critic feedback. "
        "Rewrite the story (still exactly 2 sentences) applying the feedback. "
        "Output only the improved story."
    ),
)

MAX_ITERATIONS = 3


@node(rerun_on_resume=True)
async def refinement_orchestrator(ctx: Context, node_input: str):
    """Write once, then loop critique -> refine until approval or cap."""
    current_story = await ctx.run_node(writer, node_input)

    for _ in range(MAX_ITERATIONS):
        feedback = await ctx.run_node(critic, current_story)

        if "APPROVED" in str(feedback):
            break

        current_story = await ctx.run_node(
            refiner,
            f"STORY:\n{current_story}\n\nFEEDBACK:\n{feedback}",
        )

    return current_story


root_agent = Workflow(
    name="EssayRefiner",
    edges=[("START", refinement_orchestrator)],
)
