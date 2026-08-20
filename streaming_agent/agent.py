"""Module 30 - agent behind the custom live-streaming client.

Live (bidirectional, low-latency) streaming uses the model's live API via
the api_server's /run_live WebSocket. Text modality works with regular
flash models; AUDIO modality requires a live/native-audio-capable model.
"""

from google.adk import Agent

# Live streaming requires a bidiGenerateContent-capable model; regular
# flash models are rejected. Available on this key (August 2026):
# gemini-3.1-flash-live-preview, gemini-2.5-flash-native-audio-latest.
root_agent = Agent(
    name="streaming_agent",
    model="gemini-3.1-flash-live-preview",
    description="Assistant for the live streaming client.",
    instruction=(
        "You are a helpful assistant in a live streaming session. "
        "Keep answers short and conversational."
    ),
)
