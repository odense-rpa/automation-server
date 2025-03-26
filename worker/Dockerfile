FROM python:3.13-slim

# Install uv and uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/


# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory in the container
WORKDIR /app

# Install system dependencies for Playwright

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get upgrade -y && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*


RUN pip install --upgrade pip

# Set environment variables to disable sandboxing
#ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright and required browsers
#RUN pip install playwright
#RUN playwright install chromium --with-deps

# Playwright is copied to specific build

# Copy requirements and install Python dependencies
#COPY requirements.txt .
#RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

RUN uv sync

# Run the main Python script
CMD ["uv","run", "main.py"]
