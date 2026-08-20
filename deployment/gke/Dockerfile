# Module 33 - container image for GKE (also usable for manual Cloud Run).
# Production note: api_server (headless REST), never `adk web`, in prod.
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --frozen --no-dev

COPY . .

EXPOSE 8080
CMD ["uv", "run", "adk", "api_server", "--host", "0.0.0.0", "--port", "8080", "."]
