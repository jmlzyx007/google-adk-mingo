"""Module 23 - artifacts: files with versions, next to state.

State (module 22) holds small key-value data; **artifacts** hold files -
text or binary `types.Part`s stored by filename with automatic versioning:

    version = await tool_context.save_artifact(name, part)   # returns int
    part    = await tool_context.load_artifact(name)          # latest (or version=)
    names   = await tool_context.list_artifacts()

Storage is pluggable like sessions: InMemoryArtifactService for dev,
GcsArtifactService(bucket_name=...) in production - tools never change.
All artifact tools are async: storage I/O must not block the event loop.
"""

from typing import Any, Dict

from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.genai import types

# A tiny valid PNG (1x1 red pixel) standing in for a real chart renderer.
_DUMMY_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108020000009077"
    "53de0000000c4944415408d763f8cfc000000301010018dd8db00000000049"
    "454e44ae426082"
)


async def extract_text(document_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Extracts the text of a raw document and stores it as an artifact.

    Args:
        document_name: Base name of the document, e.g. "q3_finances".
    """
    # Simulated extraction - a real pipeline would parse a PDF/scan here.
    extracted = (
        f"[extracted content of '{document_name}']\n"
        "Revenue grew 12% quarter over quarter. Operating costs fell 3%. "
        "The board approved the new hiring plan. Risks: currency exposure."
    )
    version = await tool_context.save_artifact(
        f"{document_name}_extracted.txt", types.Part.from_text(text=extracted)
    )
    return {"status": "success", "artifact": f"{document_name}_extracted.txt", "version": version}


async def summarize_document(document_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Summarizes a previously extracted document and saves the summary.

    Requires extract_text to have run first.

    Args:
        document_name: Base name of the document.
    """
    extracted = await tool_context.load_artifact(f"{document_name}_extracted.txt")
    if extracted is None:
        return {"status": "error", "message": f"No extracted text for '{document_name}'. Run extract_text first."}

    text = extracted.text or ""
    summary = "SUMMARY: " + ". ".join(text.split(". ")[:2]) + "."
    version = await tool_context.save_artifact(
        f"{document_name}_summary.txt", types.Part.from_text(text=summary)
    )
    return {"status": "success", "artifact": f"{document_name}_summary.txt", "version": version}


async def generate_chart(document_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Generates a chart image for the document and saves it as a binary artifact.

    Args:
        document_name: Base name of the document.
    """
    version = await tool_context.save_artifact(
        f"{document_name}_chart.png",
        types.Part.from_bytes(data=_DUMMY_PNG, mime_type="image/png"),
    )
    return {"status": "success", "artifact": f"{document_name}_chart.png", "version": version}


async def create_report(document_name: str, tool_context: ToolContext) -> Dict[str, Any]:
    """Compiles all artifacts of a document into a final report artifact.

    Args:
        document_name: Base name of the document.
    """
    names = await tool_context.list_artifacts()
    related = [n for n in names if n.startswith(document_name)]

    lines = [f"# Report: {document_name}", "", "## Included artifacts"]
    for name in related:
        part = await tool_context.load_artifact(name)
        if part is None:
            continue
        if part.text is not None:
            lines.append(f"- {name} (text): {part.text[:80]}...")
        elif part.inline_data is not None:
            mime = part.inline_data.mime_type
            size = len(part.inline_data.data or b"")
            lines.append(f"- {name} (binary, {mime}, {size} bytes)")

    version = await tool_context.save_artifact(
        f"{document_name}_report.md", types.Part.from_text(text="\n".join(lines))
    )
    return {
        "status": "success",
        "artifact": f"{document_name}_report.md",
        "version": version,
        "artifacts_included": related,
    }


root_agent = Agent(
    name="doc_processor",
    model="gemini-3.6-flash",
    description="Document processing pipeline with artifact versioning.",
    instruction="""
    You are a document processing assistant. When asked to process a document,
    run the full pipeline IN ORDER:
    1. extract_text
    2. summarize_document
    3. generate_chart
    4. create_report
    Then tell the user which artifacts were produced (names and versions).
    """,
    tools=[extract_text, summarize_document, generate_chart, create_report],
)
