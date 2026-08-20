"""Module 35 - deploy an agent to Vertex AI Agent Runtime (NOT YET RUN).

Fully managed: no container, no server - hand the App object to
agent_engines.create() and Google hosts it (sessions included).

Requires: uv add "google-cloud-aiplatform[adk,agent_engines]>=1.111",
a GCS staging bucket, and ADC auth.

Run from the repo root: uv run python deployment/agent_engine/deploy.py
"""

import vertexai
from vertexai import agent_engines

from google.adk.apps import App
from calculator_agent.agent import root_agent  # deploying our module 9 agent

PROJECT_ID = "your-gcp-project-id"
LOCATION = "us-central1"
STAGING_BUCKET = "gs://your-unique-bucket-name"
AGENT_DISPLAY_NAME = "calculator-agent"


def main():
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)

    app = App(name="calculator_app", root_agent=root_agent)

    remote_app = agent_engines.create(
        agent_engine=app,
        display_name=AGENT_DISPLAY_NAME,
        requirements=["google-cloud-aiplatform[adk,agent_engines]>=1.111"],
    )

    print(f"Deployment complete. Resource Name: {remote_app.resource_name}")
    print(f"Agent Runtime ID: {remote_app.resource_name.split('/')[-1]}")


if __name__ == "__main__":
    main()
