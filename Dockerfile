# Multi-stage Dockerfile for FenixAI Trading Bot
# Optimized for external Ollama service connectivity

# Build stage
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r fenixai && useradd -r -g fenixai fenixai

# Create app directory and subdirectories
WORKDIR /app
RUN mkdir -p /app/logs /app/cache /app/memory && \
    chown -R fenixai:fenixai /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=fenixai:fenixai . /app/

# Create .env from example if it doesn't exist
RUN if [ ! -f /app/.env ]; then cp /app/.env.example /app/.env; fi

# Switch to non-root user
USER fenixai

# Health check to verify Ollama connectivity
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; import os; from dotenv import load_dotenv; load_dotenv(); \
         requests.get(os.getenv('OLLAMA_BASE_URL', 'http://192.168.1.100:11434') + '/api/version', timeout=5)"

# Expose port (if needed for web interfaces)
EXPOSE 8020

# Default command - can be overridden
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8020"]
