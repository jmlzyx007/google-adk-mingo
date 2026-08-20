"""Module 28 - the CONSUMER side: ADK agent using our custom MCP server.

Identical consumption pattern to module 27 - the agent cannot tell whether
the server behind the toolset is Google's filesystem server or 90 lines of
our own Python. That symmetry is what a protocol buys.
"""

import os
import sys

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

SERVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cart_server.py")

root_agent = Agent(
    model="gemini-3.6-flash",
    name="shopping_assistant",
    instruction=(
        "You are a shopping assistant. Help the user by adding items to "
        "their cart and showing them their cart contents."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    # sys.executable = the venv's python, so the subprocess
                    # sees the same installed packages (mcp).
                    command=sys.executable,
                    args=[SERVER_PATH],
                ),
                timeout=30.0,
            ),
        )
    ],
)
