"""Module 14 - third-party tools: LangChain's Wikipedia tool in ADK.

LangchainTool is an adapter: any LangChain-compatible tool becomes an ADK
tool, opening the whole LangChain ecosystem without rewriting integrations.
"""

from google.adk import Agent
from google.adk.integrations.langchain import LangchainTool
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=2000)
wikipedia_tool = LangchainTool(tool=WikipediaQueryRun(api_wrapper=api_wrapper))

root_agent = Agent(
    name="fact_finder_agent",
    model="gemini-3.6-flash",
    description="An agent that can look up information on Wikipedia.",
    instruction="""You are a helpful fact-finding assistant.
If the user asks a question about a specific topic, person, or event,
you MUST use the Wikipedia tool to find an accurate answer.
Summarize the information you find in a clear and concise way.""",
    tools=[wikipedia_tool],
)
