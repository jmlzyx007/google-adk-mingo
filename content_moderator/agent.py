"""Module 26 - callbacks and guardrails: agent-level lifecycle hooks.

Same hook names as module 25's plugins, but attached to ONE agent via
constructor args instead of the whole App. Rule of thumb: plugin = fleet
policy (every agent in the app), callback = this agent's own behavior.

The short-circuit contract per hook:

    before_agent  -> return types.Content  => skip the whole agent turn
    before_model  -> return LlmResponse    => skip the LLM call
    after_model   -> return LlmResponse    => replace the model's response
    before_tool   -> return dict           => skip the tool, use dict as result
    after_agent   -> return None           => observe only
"""

import re
from typing import Any, Dict, Optional

from dotenv import load_dotenv

load_dotenv()

from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types

BLOCKED_WORDS = ["unsafe", "offensive"]


# --- Callback 1: response caching (check) ---
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """Returns the cached response (skipping the whole turn) on a cache hit.

    Deliberately crude lab cache: it replays the LAST answer for ANY new
    message. Real caching would key on the normalized query.
    """
    cached_text = callback_context.state.get("cached_response")
    if cached_text:
        print("[CACHE HIT] Returning saved result, skipping LLM.")
        return types.Content(
            parts=[types.Part(text=f"[CACHED]: {cached_text}")], role="model"
        )
    return None


# --- Callback 2: response caching (save) ---
def after_agent_callback(callback_context: CallbackContext) -> None:
    """Persists the final model response to session state for future hits."""
    for event in reversed(callback_context.session.events):
        if event.author != "user" and event.content and event.content.parts:
            text = event.content.parts[0].text
            if text:
                callback_context.state["cached_response"] = text
                print("[CACHE SAVE] Result persisted to session state.")
                break


# --- Callback 3: input guardrail ---
def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    """Short-circuits the LLM call when the prompt contains blocked words."""
    user_text = "".join(
        p.text
        for c in (llm_request.contents or [])
        for p in (c.parts or [])
        if p.text
    )
    for word in BLOCKED_WORDS:
        if word in user_text.lower():
            print(f"[GUARDRAIL] Blocked prompt containing: {word}")
            return LlmResponse(
                content=types.Content(
                    parts=[types.Part(text="I'm sorry, I cannot process offensive prompts.")],
                    role="model",
                )
            )
    return None


# --- Callback 4: output filtering ---
def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    """Redacts email addresses from model responses before anyone sees them."""
    if not llm_response.content or not llm_response.content.parts:
        return None
    original = llm_response.content.parts[0].text
    if not original:
        return None
    redacted = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[EMAIL_REDACTED]",
        original,
    )
    if redacted != original:
        print("[FILTER] Redacted PII from model response.")
        return llm_response.model_copy(
            update={
                "content": types.Content(parts=[types.Part(text=redacted)], role="model")
            }
        )
    return None


# --- Callback 5: tool argument validation ---
def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict[str, Any]]:
    """Rejects tool calls with out-of-policy arguments before execution."""
    if tool.name == "generate_text":
        count = args.get("word_count", 0)
        if count > 5000:
            print(f"[VALIDATION] Blocked tool call: word_count {count} exceeds limit.")
            return {
                "status": "error",
                "message": "Word count exceeds the maximum limit of 5000.",
            }
    return None


def generate_text(topic: str, word_count: int) -> dict:
    """Generates text on a topic with a word-count constraint.

    Args:
        topic: Subject of the text.
        word_count: Desired length in words (max 5000).
    """
    return {"status": "success", "text": f"A {word_count}-word essay on {topic}..."}


root_agent = Agent(
    name="secure_moderator",
    model="gemini-3.6-flash",
    instruction="You are a professional content assistant.",
    tools=[generate_text],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
)
