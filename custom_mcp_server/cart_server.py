"""Module 28 - the PROVIDER side of MCP: a custom shopping-cart server.

Built with the low-level MCP Server SDK over stdio. Any MCP client can use
it - our ADK agent, Claude Desktop, an IDE - the server neither knows nor
cares. That decoupling is the point of the protocol.

State note: carts live in this process's memory, keyed by session_id.
The consuming toolset spawns one server subprocess and keeps the session
open, so state persists across turns - but dies with the process.
Production would back this with Redis/Firestore.

Run standalone (it waits silently on stdio - that's normal):
    uv run python custom_mcp_server/cart_server.py
"""

import asyncio
import json

import mcp.server.stdio
from mcp.server import Server
from mcp.types import TextContent, Tool

SESSION_CARTS: dict[str, list[str]] = {}

app = Server("shopping-cart")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add_item_to_cart",
            description="Adds a single item to the user's shopping cart.",
            inputSchema={
                "type": "object",
                "properties": {
                    "item": {"type": "string", "description": "The item to add."},
                    "session_id": {
                        "type": "string",
                        "description": "Cart identifier; defaults to 'default'.",
                    },
                },
                "required": ["item"],
            },
        ),
        Tool(
            name="view_cart",
            description="Shows all the items currently in the user's shopping cart.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Cart identifier; defaults to 'default'.",
                    },
                },
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    session_id = arguments.get("session_id") or "default"
    cart = SESSION_CARTS.setdefault(session_id, [])

    if name == "add_item_to_cart":
        item = arguments["item"]
        cart.append(item)
        result = {"status": "success", "message": f"Added '{item}'.", "cart_size": len(cart)}
    elif name == "view_cart":
        result = {"status": "success", "items": cart, "count": len(cart)}
    else:
        result = {"status": "error", "message": f"Unknown tool: {name}"}

    return [TextContent(type="text", text=json.dumps(result))]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
