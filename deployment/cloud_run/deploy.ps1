# Module 32 - deploy an agent to Cloud Run (NOT YET RUN - needs GCP setup)
#
# Prerequisites: gcloud CLI, authenticated, project with billing,
# and the caller having Editor/Owner (Cloud Build needs Artifact Registry
# Writer + Cloud Run Admin).

$PROJECT = "your-gcp-project-id"
$REGION = "us-central1"
$AGENT = "support_analyzer"   # any agent folder in this repo

gcloud config set project $PROJECT

# adk deploy automates: containerize -> gcloud builds submit -> push to
# Artifact Registry -> gcloud run deploy. Output ends with the Service URL.
uv run adk deploy cloud_run `
    --project $PROJECT `
    --region $REGION `
    --service_name "$AGENT-service" `
    --with_ui `
    $AGENT

# --with_ui serves the dev UI at the service URL (handy for testing).
# Production: omit --with_ui for a headless REST API (module 33's lesson),
# and pass GOOGLE_API_KEY / Vertex settings as env vars, e.g.:
#   --set-env-vars GOOGLE_GENAI_USE_VERTEXAI=1,GOOGLE_CLOUD_PROJECT=$PROJECT
