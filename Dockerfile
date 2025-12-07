# Multi-stage build using uv for blazingly fast installs

################################
# UV BUILDER
# Install dependencies using uv
################################
FROM ghcr.io/astral-sh/uv:0.9.13 AS builder
WORKDIR /app

# Copy pyproject and lock file
COPY pyproject.toml uv.lock ./

# Install dependencies only (no dev dependencies for production)
# --no-extra: Exclude development dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-extra

################################
# PRODUCTION
# Final image with Python runtime
################################
FROM python:3.13.7-slim

RUN apt-get update && apt-get install --no-install-recommends -y \
    curl

# Copy virtualenv from uv image
COPY --from=builder /app/.venv /app/.venv

# Copy application
COPY . /app/
WORKDIR /app

# Use virtualenv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Run the application
CMD ["python", "-m", "python_web_service_boilerplate"]
