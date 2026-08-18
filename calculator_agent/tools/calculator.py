"""Module 9 - custom function tools.

Each tool is a plain Python function: ADK inspects the signature (type hints)
and docstring to generate the schema the LLM sees. Structured returns
(Pydantic model with a status field) let the agent distinguish success
from failure instead of crashing.
"""

from pydantic import BaseModel


class MathResult(BaseModel):
    status: str
    result: float = 0
    message: str | None = None


def add(a: int, b: int) -> MathResult:
    """Adds two numbers together.

    Use this tool when the user asks for a sum or addition.

    Args:
        a: The first number.
        b: The second number.
    """
    return MathResult(status="success", result=a + b)


def subtract(a: int, b: int) -> MathResult:
    """Subtracts the second number from the first.

    Args:
        a: The number to subtract from.
        b: The number to subtract.
    """
    return MathResult(status="success", result=a - b)


def multiply(a: int, b: int) -> MathResult:
    """Multiplies two numbers together.

    Args:
        a: The first factor.
        b: The second factor.
    """
    return MathResult(status="success", result=a * b)


def divide(a: int, b: int) -> MathResult:
    """Divides the first number by the second.

    Returns an error status instead of raising when dividing by zero.

    Args:
        a: The dividend.
        b: The divisor.
    """
    if b == 0:
        return MathResult(status="error", message="Cannot divide by zero.")
    return MathResult(status="success", result=a / b)
