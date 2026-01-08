# Multi-stage build for Project Synapse
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Create non-root user
RUN groupadd -r synapse && useradd -r -g synapse synapse

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/synapse/.local

# Copy application code
COPY synapse/ ./synapse/
COPY config/ ./config/
COPY setup.py .
COPY README.md .

# Install the package
RUN pip install -e .

# Change ownership to synapse user
RUN chown -R synapse:synapse /app

# Switch to non-root user
USER synapse

# Add local bin to PATH
ENV PATH=/home/synapse/.local/bin:$PATH

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["synapse", "server", "start", "--host", "0.0.0.0", "--port", "8080"]