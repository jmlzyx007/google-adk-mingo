"""Module 13 - ToolContext.actions: business rules enforced in Python.

The $10,000 limit lives in the runtime, not in the prompt. The LLM cannot
talk its way past an `if` statement: `tool_context.actions.transfer_to_agent`
hands the conversation to a registered sub-agent regardless of what the
model intended.
"""

from google.adk.tools import ToolContext


def execute_investment(amount: float, tool_context: ToolContext) -> str:
    """Executes a long-term investment for the user.

    Investments above $10,000 are escalated to a supervisor automatically.

    Args:
        amount: The investment amount in USD.
    """
    if amount > 10000:
        tool_context.actions.transfer_to_agent = "supervisor"
        return f"Investment of ${amount} exceeds limit. Escalating..."

    return f"Success! ${amount} invested in portfolio."
