"""Module 34 - the module 28 cart server adapted for Cloud Run (NOT YET RUN).

Two changes vs the stdio version:
1. Transport: streamable HTTP instead of stdio - Cloud Run speaks HTTP,
   nobody spawns subprocesses there.
2. State: per-session JSON files under /tmp. Works for the lab but /tmp is
   the container's volatile filesystem - instances scale to zero and state
   dies with them. Production: Redis / Firestore keyed by session_id.

Local test: uv run python deployment/mcp_cloud_run/stateless_cart_server.py
"""

import json
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

CART_DIR = Path("/tmp/carts") if os.name != "nt" else Path(os.getenv("TEMP", ".")) / "carts"
CART_DIR.mkdir(parents=True, exist_ok=True)

mcp = FastMCP("shopping-cart", host="0.0.0.0", port=int(os.getenv("PORT", "8080")))


def get_cart(session_id: str) -> list[str]:
    f = CART_DIR / f"{session_id}.json"
    return json.loads(f.read_text()) if f.exists() else []


def save_cart(session_id: str, cart: list[str]) -> None:
    (CART_DIR / f"{session_id}.json").write_text(json.dumps(cart))


@mcp.tool()
def add_item_to_cart(item: str, session_id: str = "default") -> dict:
    """Adds a single item to the user's shopping cart."""
    cart = get_cart(session_id)
    cart.append(item)
    save_cart(session_id, cart)
    return {"status": "success", "message": f"Added '{item}'.", "cart_size": len(cart)}


@mcp.tool()
def view_cart(session_id: str = "default") -> dict:
    """Shows all the items currently in the user's shopping cart."""
    cart = get_cart(session_id)
    return {"status": "success", "items": cart, "count": len(cart)}


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
