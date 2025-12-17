# Multi-stage build for Cloud-Anomaly-Detection

# ========== BUILDER STAGE ==========
FROM python:3.10-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ========== DEVELOPMENT STAGE ==========
FROM python:3.10-slim as development

WORKDIR /app

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY src/ ./src/
COPY requirements.txt .
COPY sample_usage.py .
COPY run.sh .

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app && \
    chmod +x run.sh
USER appuser

# Expose port
EXPOSE 8000

# Development command (with hot reload)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ========== PRODUCTION STAGE ==========
FROM python:3.10-slim as production

WORKDIR /app

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy only necessary files
COPY src/ ./src/
COPY requirements.txt .
COPY run.sh .

# Create non-root user and directories
RUN useradd -m -u 1000 appuser && \
    mkdir -p logs && \
    chown -R appuser:appuser /app && \
    chmod +x run.sh
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=2)" || exit 1

# Production command
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]