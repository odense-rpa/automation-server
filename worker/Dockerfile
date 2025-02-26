FROM python:3.13-slim

# Install uv and uvx
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory in the container
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get upgrade && apt-get install -y git

RUN pip install --upgrade pip

# Set environment variables to disable sandboxing
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright and required browsers
RUN pip install playwright
#RUN playwright install-deps
RUN playwright install --with-deps


# Copy requirements and install Python dependencies
#COPY requirements.txt .
#RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

RUN uv sync

# Run the main Python script
CMD ["uv","run", "main.py"]
