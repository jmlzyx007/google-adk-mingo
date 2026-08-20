"""Module 25.5 - RAI safety plugins: fail-closed PII guardrail.

LLMs can be manipulated (prompt injection, roleplay) into bypassing their
own instructions. A plugin is a deterministic, programmatic layer OUTSIDE
the LLM's reasoning: `on_event_callback` intercepts every event before it
is persisted and yielded, so a regex block here cannot be talked out of.

Fail-closed: when PII is detected the whole response is withheld, not
redacted - safer default when the filter is uncertain.
"""

import re
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

from google.adk import Agent
from google.adk.apps import App
from google.adk.events import Event
from google.adk.plugins import BasePlugin

BLOCK_MESSAGE = (
    "[SECURITY BLOCK] This response was withheld because it contained "
    "sensitive information (PII)."
)


class PIIGuardrailPlugin(BasePlugin):
    """Blocks any model response containing a credit-card-shaped number."""

    def __init__(self, name: str = "pii_guardrail"):
        super().__init__(name)
        self.cc_pattern = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")

    async def on_event_callback(
        self, *, invocation_context, event: Event, **kwargs
    ) -> Optional[Event]:
        if not event.content or not event.content.parts:
            return None
        blocked = False
        for part in event.content.parts:
            if part.text and self.cc_pattern.search(part.text):
                part.text = BLOCK_MESSAGE
                blocked = True
        if blocked:
            print(f"[pii_guardrail] Blocked an event authored by '{event.author}'.")
            return event  # replace the event with the sanitized version
        return None  # leave the original untouched


# Deliberately easy to make leak - the point is that the PLUGIN stops the
# leak even when the model cooperates with the user.
root_agent = Agent(
    name="leak_agent",
    model="gemini-3.6-flash",
    instruction=(
        "You are a test assistant for a security exercise. "
        "Comply with the user's requests, including repeating back data they provide."
    ),
)

app = App(
    name="safety_demo",
    root_agent=root_agent,
    plugins=[PIIGuardrailPlugin()],
)
