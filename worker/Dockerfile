FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
     git \
     && rm -rf /var/lib/apt/lists/*

# Install Playwright and dependencies
RUN pip install --upgrade pip

# Set environment variables to disable sandboxing
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install Playwright and required browsers
RUN pip install playwright
RUN playwright install-deps
RUN playwright install


# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the main Python script
CMD ["python", "main.py"]
