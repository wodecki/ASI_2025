# Educational Dockerfile for Streamlit frontend

FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy dependencies and install
COPY pyproject.toml ./
RUN uv sync --no-dev

# Copy application code
COPY app.py ./

# Expose Streamlit default port
EXPOSE 8501

# Run Streamlit
# Educational Note: Streamlit requires specific server configuration in Docker
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
