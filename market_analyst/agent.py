"""Module 11 - OpenAPI tools: currency agent over the Frankfurter API.

Instead of hand-writing HTTP tool functions, an OpenAPI spec is handed to
OpenAPIToolset, which generates one tool per operation (here:
`get_latest_rates` from operationId). ADK builds the request, calls the
REST endpoint, and returns the JSON to the model.
"""

import json

from google.adk import Agent
from google.adk.tools.openapi_tool import OpenAPIToolset

FRANKFURTER_SPEC = {
    "openapi": "3.0.0",
    "info": {
        "title": "Frankfurter Currency API",
        "description": "Free API for current and historical foreign exchange rates",
        "version": "1.0.0",
    },
    "servers": [{"url": "https://api.frankfurter.app"}],
    "paths": {
        "/latest": {
            "get": {
                "operationId": "get_latest_rates",
                "summary": "Get latest exchange rates",
                "parameters": [
                    {
                        "name": "amount",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "number"},
                    },
                    {
                        "name": "from",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                    {
                        "name": "to",
                        "in": "query",
                        "required": False,
                        "schema": {"type": "string"},
                    },
                ],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {"schema": {"type": "object"}}
                        },
                    }
                },
            }
        }
    },
}

currency_toolset = OpenAPIToolset(
    spec_str=json.dumps(FRANKFURTER_SPEC),
    spec_str_type="json",
)

root_agent = Agent(
    name="market_analyst",
    model="gemini-3.6-flash",
    description="A specialist in global currency exchange rates.",
    instruction="""You are an expert Global Market Analyst.
Use the `get_latest_rates` tool to convert currencies and check exchange rates for the user.
Always state the amount, the original currency, and the converted currency clearly.""",
    tools=[currency_toolset],
)
