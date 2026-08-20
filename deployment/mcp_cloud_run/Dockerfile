# Module 34 - MCP server as a Cloud Run service (NOT YET RUN)
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir "mcp<2"
COPY stateless_cart_server.py .
EXPOSE 8080
CMD ["python", "stateless_cart_server.py"]
