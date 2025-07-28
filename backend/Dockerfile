# Build stage
FROM python:3.13-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv sync --frozen --no-install-workspace

# Copy application code
COPY . .

# Install the project
RUN uv sync --frozen

# Runtime stage
FROM python:3.13-slim AS runtime

# Install uv for runtime
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    mkdir -p /app /data && \
    chown -R appuser:appuser /app /data

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    UV_SYSTEM_PYTHON=1

# Set working directory
WORKDIR /app

# Copy virtual environment and application from builder
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
COPY --from=builder --chown=appuser:appuser /app /app

# Copy configuration files
COPY --chown=appuser:appuser scripts/entry-point.sh /app/entry-point.sh

# Remove any .env file that might have been copied
RUN rm -f .env

# Make entry-point executable
RUN chmod +x /app/entry-point.sh

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Add metadata labels
LABEL maintainer="your-email@example.com" \
      version="0.2.0" \
      description="Automation Server Backend"

# Use exec form for proper signal handling
ENTRYPOINT ["/app/entry-point.sh"]