FROM python:3.13.5-slim AS builder

ARG APPDIR=/home/appuser/app

WORKDIR $APPDIR

# Install uv for dependency management
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Generate virtual environment with runtime dependencies
RUN uv sync --no-dev
# Create non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

#WORKDIR $APPDIR

# Copy virtual environment from builder and add it to the path
ENV PATH=$APPDIR/.venv/bin:$PATH

# Copy application code
COPY src/ ./src
COPY scripts/ ./scripts
COPY production.env ./

# Give ownership of /app to appuser
RUN chown appuser:appgroup -R ../app

# Switch to non-root user
USER appuser

# Expose the port the API runs on
EXPOSE 8000

# Make sure Python knows where to look for imports
ENV PYTHONPATH=$APPDIR/src

# Initialize the database
RUN python scripts/init_db.py

# Run the API
CMD ["gunicorn", "app.app:app", \
    "--workers", "4", \
    "--worker-class", "uvicorn.workers.UvicornWorker", \
    "--bind", "0.0.0.0:8000"]