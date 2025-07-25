# Base stage with common setup
FROM python:3.13-slim AS base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

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
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "main.py" || exit 1

# Add metadata labels
LABEL maintainer="miwn@odense.dk" \
      version="0.2.0" \
      description="Automation Server Worker"

# Run the main Python script
CMD ["uv", "run", "main.py"]

# Playwright worker stage
FROM base AS worker-playwright

# Switch back to root for Playwright installation
USER root

# Install Playwright system dependencies
# RUN apt-get update && \
#     apt-get install -y --no-install-recommends \
#         wget \
#         fonts-liberation \
#         libappindicator3-1 \
#         libasound2 \
#         libatk-bridge2.0-0 \
#         libatspi2.0-0 \
#         libdrm2 \
#         libgtk-3-0 \
#         libnspr4 \
#         libnss3 \
#         libx11-xcb1 \
#         libxcomposite1 \
#         libxdamage1 \
#         libxrandr2 \
#         xdg-utils \
#         libxss1 \
#         libgconf-2-4 \
#     && rm -rf /var/lib/apt/lists/*

# Set Playwright environment
ENV PLAYWRIGHT_BROWSERS_PATH=/playwright

# Install Playwright and browsers as root
RUN pip install playwright && \
    playwright install chromium --with-deps

# Create playwright directory and set permissions
RUN mkdir -p /playwright && \
    chown -R worker:worker /playwright

# Switch back to worker user
USER worker

# Add health check - verify main.py process is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD pgrep -f "main.py" || exit 1

# Add metadata labels
LABEL maintainer="miwn@odense.dk" \
      version="0.2.0" \
      description="Automation Server Worker with Playwright"

# Run the main Python script
CMD ["uv", "run", "main.py"]