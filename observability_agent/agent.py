"""Module 25 - observability: plugins + OpenTelemetry.

Three observability layers:
1. Custom business plugin (AlertingPlugin) - domain alerting logic that runs
   OUTSIDE the LLM, hooked into the runner lifecycle.
2. Enterprise telemetry - OpenTelemetry exporters to Cloud Trace/Monitoring
   (enabled only when ENABLE_GCP_TELEMETRY=1 and GCP creds exist).
3. Native events - everything the Trace tab shows is already an event stream.

Plugins attach to the App, not the Agent: cross-cutting concerns stay out of
agent code entirely.

ADK 2.7 note: the lab's `event.event_type == 'request_error'` API does not
exist - the real hooks are dedicated callbacks (`on_model_error_callback`,
`after_model_callback`, `on_event_callback`, ...).
"""

import os

from dotenv import load_dotenv

load_dotenv()

from google.adk import Agent
from google.adk.apps import App
from google.adk.plugins import BasePlugin


class AlertingPlugin(BasePlugin):
    """Alerts after N consecutive model errors; resets on success."""

    def __init__(self, name: str = "alerting_plugin", threshold: int = 3):
        super().__init__(name)
        self.error_threshold = threshold
        self.consecutive_errors = 0

    async def after_model_callback(self, *, callback_context, llm_response, **kwargs):
        # A successful model response breaks the error streak.
        self.consecutive_errors = 0
        return None

    async def on_model_error_callback(self, *, callback_context, llm_request, error, **kwargs):
        self.consecutive_errors += 1
        print(
            f"[ALERT] Model error ({self.consecutive_errors}/{self.error_threshold}): {error}"
        )
        if self.consecutive_errors >= self.error_threshold:
            print("[CRITICAL ALERT] Persistent errors detected! Page the on-call.")
        # Returning None re-raises the error; returning an LlmResponse would
        # swallow it (fallback pattern).
        return None


# --- Enterprise telemetry (optional: needs GCP project + ADC) ---
if os.getenv("ENABLE_GCP_TELEMETRY") == "1":
    from google.adk.telemetry.google_cloud import get_gcp_exporters
    from google.adk.telemetry.setup import maybe_set_otel_providers

    otel_hooks = get_gcp_exporters(
        enable_cloud_tracing=True,
        enable_cloud_metrics=True,
    )
    maybe_set_otel_providers(otel_hooks_to_setup=[otel_hooks])


root_agent = Agent(
    name="monitored_agent",
    model="gemini-3.6-flash",
    instruction="Answer the user's questions clearly and briefly.",
)

app = App(
    name="observability_demo",
    root_agent=root_agent,
    plugins=[AlertingPlugin()],
)
