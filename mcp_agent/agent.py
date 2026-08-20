"""Module 27 - intro to MCP: consuming an external MCP server as tools.

MCP (Model Context Protocol) standardizes how tool servers expose
capabilities. MCPToolset connects to a server, discovers its tools
dynamically, and adapts every one of them into ADK tools - like module 14's
LangchainTool, but protocol-level: any MCP server (thousands exist) plugs in
without a Python adapter per tool.

Here: the official filesystem server, spawned as a subprocess over stdio
(`npx @modelcontextprotocol/server-filesystem <dir>`). Two security layers:
- the sandbox dir passed to the server is a hard boundary for file access;
- `tool_filter` exposes only read operations to the LLM (no write/delete).
"""

import os

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

TARGET_FOLDER_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "test_files"
)

root_agent = Agent(
    model="gemini-3.6-flash",
    name="filesystem_agent",
    instruction=(
        "You are a helpful assistant that can interact with a user's local "
        "file system. You can list files and read their content."
    ),
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        os.path.abspath(TARGET_FOLDER_PATH),
                    ],
                ),
                # First run downloads the server via npx - the default 5s
                # session timeout is too short for that.
                timeout=60.0,
            ),
            tool_filter=["list_directory", "read_file"],
        )
    ],
)
