# Deployment operational guide (Part 6, modules 31–36)

Status: **prepared, not executed** — every artifact in [deployment/](../deployment/) is
ready to run once the GCP prerequisites below exist. This guide is the resume of the six
modules' operations.

## One-time GCP prerequisites (blocks modules 13.5, 25 telemetry, and all of Part 6)

1. Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install).
2. Create a project with **billing enabled**.
3. Authenticate: `gcloud auth login` and `gcloud auth application-default login`.
4. `gcloud config set project <project-id>` and add `GOOGLE_CLOUD_PROJECT=<project-id>` to `.env`.
5. Enable APIs as prompted (Cloud Run, Cloud Build, Artifact Registry, Vertex AI, GKE).

## Module 31 — choosing a deployment strategy

ADK's philosophy is **platform-first security**: lean on the platform's TLS, DDoS
protection, and IAM instead of writing security code.

| Option | Best for | Trade-off |
|---|---|---|
| **Cloud Run** (`adk deploy cloud_run`) | MVPs, standard apps — deployed in ~5 min, pay-per-use, auto-HTTPS | least control |
| **Agent Runtime** (Vertex AI managed) | enterprise/regulated (FedRAMP, HIPAA), OAuth, managed sessions | most opinionated |
| **GKE** | orgs already on Kubernetes, custom networking, GPUs | you operate everything |
| **Custom FastAPI on Cloud Run** | non-standard auth (LDAP...) | you own the server code |

Rule of thumb: speed/cost → Cloud Run; compliance → Agent Runtime; control → GKE.

## Module 32 — Cloud Run (`deployment/cloud_run/deploy.ps1`)

One command does containerize → `gcloud builds submit` → Artifact Registry →
`gcloud run deploy`, and prints the public Service URL:

```sh
uv run adk deploy cloud_run --project <id> --region us-central1 --with_ui <agent_folder>
```

`--with_ui` serves the dev UI at the URL (testing); omit it in production (headless API).
IAM: Cloud Build's service account needs Artifact Registry Writer + Cloud Run Admin.

## Module 33 — GKE (`deployment/gke/`)

Manual version of the same pipeline: `Dockerfile` (runs `adk api_server`, **never**
`adk web` in production) → `gcloud builds submit` → Autopilot cluster →
`kubectl apply -f deployment.yaml -f service.yaml` → watch for the LoadBalancer IP.
Troubleshooting: `ImagePullBackOff` = registry perms; `CrashLoopBackOff` = `kubectl logs`.
**Delete the cluster after the lab — it bills while it exists.**

## Module 34 — MCP server on Cloud Run (`deployment/mcp_cloud_run/`)

The module 28 cart server with two adaptations:
- **Transport**: streamable HTTP instead of stdio (Cloud Run speaks HTTPS, not subprocesses).
- **State**: `/tmp` JSON per session — volatile; production wants Redis/Firestore.

Agents connect with the same toolset, different params:
`MCPToolset(connection_params=StreamableHTTPConnectionParams(url="https://.../mcp"))` —
tool logic now scales independently of every agent using it.

## Module 35 — Agent Runtime (`deployment/agent_engine/`)

No container at all: `agent_engines.create(agent_engine=App(...), ...)` uploads the agent
and Google hosts it, sessions included. `deploy.py` ships our `calculator_agent`;
`interact.py` opens a remote session and streams a query. Needs
`google-cloud-aiplatform[adk,agent_engines]>=1.111` and a GCS staging bucket.

## Module 36 — Gemini Enterprise (formerly AgentSpace)

The operations layer above all of this: managed hosting + governance (RBAC, audit,
HIPAA/FedRAMP), enterprise data connectors (Drive, SharePoint, Salesforce, BigQuery) for
RAG grounding, an internal **Agent Gallery** marketplace, and a no-code Agent Designer.
Workflow: build/test locally with ADK → deploy → register for discovery and monitoring.
Governance caveat: no-code creation lets non-developers bypass guardrails — platform
monitoring matters.

## Suggested first deployment (when GCP is ready)

`support_analyzer` via module 32's script — smallest agent with structured output, and the
`--with_ui` dev UI at the public URL makes success obvious in one glance.
