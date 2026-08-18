"""Module 12 - built-in tools and grounding: research assistant.

Mixes the built-in `google_search` (grounding: answers backed by live web
results) with custom function tools in a single agent - a combination
Gemini 2+ models support.
"""

from datetime import datetime

from google.adk import Agent
from google.adk.tools import google_search


def format_research_notes(topic: str, findings: str) -> dict:
    """Formats research findings into a structured document.

    Use this as the final step to compile findings into a report.

    Args:
        topic: The research topic used as the report title.
        findings: The full findings text to include in the report.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    document = f"""# Research Report: {topic}
Generated: {timestamp}
## Findings
{findings}""".strip()
    return {"status": "success", "document": document}


def extract_key_facts(text: str, num_facts: int = 5) -> dict:
    """Extracts key sentences from a block of text.

    Args:
        text: The text to extract facts from.
        num_facts: Maximum number of facts to return.
    """
    sentences = text.split(".")
    facts = [s.strip() for s in sentences if len(s.strip()) > 10][:num_facts]
    return {"status": "success", "facts": facts}


root_agent = Agent(
    model="gemini-3.6-flash",
    name="research_assistant",
    description="Conducts web research and compiles findings",
    instruction="""You are an expert research assistant.
You have access to the web via `google_search` and custom text processing tools.
When given a research topic, follow this workflow:
1. Use `google_search` to find current information.
2. Use `extract_key_facts` to pull important points.
3. Use `format_research_notes` to compile into a professional report.
4. Present the final formatted document.""",
    tools=[
        google_search,
        extract_key_facts,
        format_research_notes,
    ],
)
