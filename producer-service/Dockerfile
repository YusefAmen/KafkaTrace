# Multi-stage build for optimized production image
# This helps you learn Docker best practices and security considerations

# Stage 1: Build stage
FROM python:3.11-slim as builder

# TODO: Add build arguments for version control
# ARG BUILD_VERSION
# ARG BUILD_DATE

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Stage 2: Production stage
FROM python:3.11-slim as production

# TODO: Add security scanning and vulnerability checks
# This helps you learn container security best practices

# Create non-root user for security
# TODO: Configure proper user permissions and capabilities
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Set working directory
WORKDIR /app

# Copy application code
COPY app.py .
COPY requirements.txt .

# TODO: Add health check for container orchestration
# This helps you learn container health monitoring
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# TODO: Add proper signal handling for graceful shutdowns
# This helps you learn container lifecycle management

# Expose port
EXPOSE 8000

# TODO: Add proper entrypoint script for initialization
# This helps you learn container startup patterns

# Run the application
CMD ["python", "app.py"]

# TODO: Add labels for better container management
# LABEL maintainer="your-email@example.com"
# LABEL version="${BUILD_VERSION}"
# LABEL build-date="${BUILD_DATE}"
# LABEL description="KafkaTrace Producer Service" 