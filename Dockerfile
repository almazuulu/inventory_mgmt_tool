# Use official Python runtime as base image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Askarbe Kalmazbekuulu"
LABEL description="Warehouse Inventory Management Tool with concurrent access support"
LABEL version="0.1.0"

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    WAREHOUSE_FILE=/app/warehouse_state.json

# Install system dependencies (if needed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install filelock>=3.12.0

# Copy source code
COPY src/ ./src/

# Install the package in editable mode
RUN pip install -e .

# Create directory for data persistence
RUN mkdir -p /app/data

# Set the state file to data directory by default
ENV WAREHOUSE_FILE=/app/data/warehouse_state.json

# Volume for persistent data
VOLUME ["/app/data"]

# Run the application
# The tool reads from stdin and writes to stdout
ENTRYPOINT ["python", "-m", "src.main"]

# Health check (optional - checks if Python can import the module)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import src.main" || exit 1


