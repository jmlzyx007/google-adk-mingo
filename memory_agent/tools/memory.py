"""Module 10 - stateful tools via ToolContext.

A tool that declares a `tool_context: ToolContext` parameter gets it injected
by ADK (the LLM never sees that parameter). `tool_context.state` is the
session state: writes are tracked as deltas on the event and persisted by
the Runner, so facts survive across turns without relying on LLM memory.
"""

from google.adk.tools import ToolContext


def store_name(name: str, tool_context: ToolContext) -> str:
    """Saves the user's name to session memory.

    Use this when the user introduces themselves.

    Args:
        name: The user's name as they stated it.
    """
    tool_context.state["user_name"] = name
    return "Got it! I've saved your name."


def recall_name(tool_context: ToolContext) -> str:
    """Retrieves the user's name from session memory.

    Use this when the user asks what their name is.
    """
    name = tool_context.state.get("user_name", "Stranger")
    return f"Your name is {name}."
