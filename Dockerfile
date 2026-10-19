# File: Dockerfile
# Purpose: Build and run the ScamShield FastAPI backend on Render with ML model support.

FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies required for building Python packages if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies first for optimal caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code, including your logistic regression model files
COPY . .

# Render dynamically injects a PORT environment variable (defaults to 10000 if not set)
# We bind Uvicorn to 0.0.0.0 and use the dynamic port
CMD uvicorn scamshield.main:app --host 0.0.0.0 --port ${PORT:-10000}