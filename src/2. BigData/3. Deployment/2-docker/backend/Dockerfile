# Educational Dockerfile for FastAPI + AutoGluon backend
# Demonstrates modern uv-based Python dependency management in Docker

FROM python:3.11-slim

# Install uv - fast Python package manager
# Educational Note: Using official uv image as source
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first (for Docker layer caching)
# Educational Note: Dependencies change less frequently than code,
# so we copy them first to leverage Docker's layer cache
COPY pyproject.toml ./

# Install dependencies
# Educational Note: uv sync reads pyproject.toml and creates .venv
RUN uv sync --no-dev

# Copy application code and model artifacts
# Educational Note: Copied after dependencies for better cache utilization
COPY main.py ./
COPY data/ ./data/
COPY autogluon-iowa-daily/ ./autogluon-iowa-daily/

# Expose port
# Educational Note: Documents which port the container listens on
EXPOSE 8003

# Environment variables
# Educational Note: PORT can be overridden at runtime (important for Cloud Run)
ENV PORT=8003

# Run the application
# Educational Note: Using exec form (JSON array) for proper signal handling
# 'uv run' automatically activates the virtual environment
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
