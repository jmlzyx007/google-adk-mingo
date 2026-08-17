import os
from functools import cached_property
from google.adk import Agent
from google.adk.models import Gemini
from google.adk.models.lite_llm import LiteLlm
from google.genai import Client, types
from pydantic import BaseModel

# Step 1: Define the ResilientGemini subclass
class ResilientGemini(Gemini):
    """
    Expert pattern: Subclass Gemini to centralize production configurations
    like project, location, and advanced retry logic.
    """
    @cached_property
    def api_client(self) -> Client:
        http_options = types.HttpOptions(
            retry_options=types.HttpRetryOptions(
                max_delay=10, # Max seconds to wait between retries
                exp_base=2.0,  # Base for exponential backoff
                jitter=0.5,    # Jitter to prevent thundering herd
            )
        )
        if os.environ.get("GOOGLE_GENAI_USE_VERTEXAI") == "1":
            # Option B: Vertex AI (project/location are only valid here)
            return Client(
                vertexai=True,
                project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
                location="us-central1",
                http_options=http_options,
            )
        # Option A: Gemini API — picks up GOOGLE_API_KEY from the environment
        return Client(http_options=http_options)

# Step 2: Implement the model selection logic
# This allows developers to toggle between cloud and local models via env vars.
if os.getenv("USE_LOCAL_MODEL") == "1":
    # Use LiteLLM abstraction for local development with Ollama
    model_to_use = LiteLlm(model="ollama_chat/mistral")
else:
    # Use the professional, native Gemini subclass for production
    model_to_use = ResilientGemini(model="gemini-3.6-flash")

class SupportAnalysis(BaseModel):
    category: str
    sentiment: str
    summary: str

root_agent = Agent(
    model=model_to_use,
    name='support_analyzer_agent',
    description='An agent that categorizes customer support tickets and extracts sentiment',
    instruction="""
        You are an expert customer support analyzer. Your task is to:
        1. Determine the category of the user's issue ("billing", "technical", or "general").
        2. Analyze the sentiment of the message ("positive", "negative", or "neutral").
        3. Write a concise, 1-sentence summary of the user's issue.
        
        You MUST respond only with a JSON object matching the requested schema. Do not try to solve their problem.
    """,
    output_schema=SupportAnalysis,
    output_key="last_ticket_analysis"
)