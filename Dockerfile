FROM python:3.11-slim

LABEL maintainer="PBJRAG Team"
LABEL description="PBJRAG WebUI with Qdrant integration"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files
COPY pyproject.toml setup.cfg README.md ./
COPY src/ ./src/

# Install PBJRAG package and dependencies
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir \
    streamlit==1.40.0 \
    plotly==5.24.1 \
    pandas==2.2.3 \
    qdrant-client==1.12.1 \
    watchdog==5.0.3

# Copy WebUI application
COPY webui/ ./webui/

# Create directories for uploads and examples
RUN mkdir -p /app/uploads /app/examples

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=watchdog

# Run Streamlit
CMD ["streamlit", "run", "webui/app.py", "--server.address=0.0.0.0"]
