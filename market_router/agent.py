"""Module 17 - structured routing: classifier output drives dictionary edges.

Routing decisions here are neither free-form LLM transfers (module 15) nor
fixed paths (module 16): a classifier emits a *structured* value constrained
by a Literal schema, and the Workflow maps that value to the next node via
a routing dictionary. The LLM classifies; the graph routes.

    START ─> classifier ─> route_currency ─┬─ "USD" ─> usd_analyst
                                           ├─ "EUR" ─> eur_analyst
                                           └─ "GBP" ─> gbp_analyst

Note: an LlmAgent node puts its validated schema object on ctx.output, but
dictionary edges match on ctx.route - so a tiny @node function bridges the
two by reading the classifier's output and emitting it as the route.
"""

from typing import Any, Literal

from pydantic import BaseModel

from google.adk import Agent, Workflow
from google.adk.agents.context import Context
from google.adk.workflow import node


class MarketRoute(BaseModel):
    currency: Literal["USD", "EUR", "GBP"]


classifier = Agent(
    name="classifier",
    model="gemini-3.6-flash",
    instruction="Extract the currency (USD, EUR, or GBP) from the user's request. Return ONLY the JSON.",
    output_schema=MarketRoute,
)

usd_analyst = Agent(
    name="usd_analyst",
    model="gemini-3.6-flash",
    instruction="Provide a brief, bullish outlook for the US Dollar.",
)

eur_analyst = Agent(
    name="eur_analyst",
    model="gemini-3.6-flash",
    instruction="Provide a brief, cautious outlook for the Euro.",
)

gbp_analyst = Agent(
    name="gbp_analyst",
    model="gemini-3.6-flash",
    instruction="Provide a brief, neutral outlook for the British Pound.",
)

@node
def route_currency(ctx: Context, node_input: Any) -> None:
    """Emits the classifier's currency as the routing value."""
    decision = node_input if node_input is not None else ctx.state.get("market_route")
    currency = getattr(decision, "currency", None) or decision["currency"]
    ctx.route = currency


root_agent = Workflow(
    name="MarketSystem",
    edges=[
        ("START", classifier),
        (classifier, route_currency),
        (route_currency, {
            "USD": usd_analyst,
            "EUR": eur_analyst,
            "GBP": gbp_analyst,
        }),
    ],
)
