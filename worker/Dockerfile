FROM python:3.10-slim

# Set working directory in the container
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libgconf-2-4 \
    libxrandr2 \
    xdg-utils \
    libgtk-3-0 \
    libxshmfence1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Playwright and dependencies
RUN pip install playwright && playwright install

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the main Python script
CMD ["python", "main.py"]
