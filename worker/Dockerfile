# Base stage with common setup
FROM python:3.13-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.11.28 /uv /uvx /bin/

# Create non-root user
RUN useradd -m -u 1001 worker && \
    mkdir -p /app && \
    chown -R worker:worker /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install basic system dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright OS-level system dependencies
ENV PLAYWRIGHT_BROWSERS_PATH=/playwright
RUN pip install playwright && \
    playwright install-deps chromium && \
    pip uninstall -y playwright

# Create playwright browser cache directory
RUN mkdir -p /playwright && \
    chown -R worker:worker /playwright

# Switch to non-root user
USER worker

# Copy dependency files
COPY --chown=worker:worker pyproject.toml uv.lock* ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY --chown=worker:worker . .

# Standard worker stage
FROM base AS worker

# Add health check - verify main.py process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python3 -c "import os, time; s=os.stat('/tmp/worker.health'); exit(0 if time.time()-s.st_mtime < 300 else 1)"

# Add metadata labels
LABEL maintainer="miwn@odense.dk" \
      version="0.4.0" \
      description="Automation Server Worker"

# Run the main Python script
CMD ["uv", "run", "main.py"]
