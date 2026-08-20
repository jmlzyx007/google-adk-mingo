# Module 34 - deploy the MCP server to Cloud Run (NOT YET RUN - needs GCP)

$PROJECT = "your-gcp-project-id"
$REGION = "us-central1"

gcloud config set project $PROJECT
gcloud run deploy cart-mcp-server `
    --source . `
    --region $REGION `
    --allow-unauthenticated   # lab only; production wants IAM/auth

# After deploy, point an ADK agent at the URL (remote MCP over HTTP):
#
#   from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
#   from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
#
#   MCPToolset(connection_params=StreamableHTTPConnectionParams(
#       url="https://cart-mcp-server-xxxx-uc.a.run.app/mcp"))
#
# Same toolset as modules 27/28 - only the transport changed
# (stdio subprocess -> HTTPS service).
