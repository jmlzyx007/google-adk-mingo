# Deployment artifacts (Part 6, modules 31-36)

Ready-to-run templates for deploying this repo's agents to Google Cloud.
**None of these have been executed yet** — they are prepared for the day the
GCP prerequisites exist (see [docs/deployment-guide.md](../docs/deployment-guide.md)).

| Folder | Module | Target |
|---|---|---|
| `cloud_run/` | 32 | Cloud Run via `adk deploy cloud_run` |
| `gke/` | 33 | GKE with Dockerfile + Kubernetes manifests |
| `mcp_cloud_run/` | 34 | The module 28 cart server as a remote MCP service |
| `agent_engine/` | 35 | Vertex AI Agent Runtime (managed) |

Module 31 (strategy comparison) and 36 (Gemini Enterprise) are covered in the guide.
