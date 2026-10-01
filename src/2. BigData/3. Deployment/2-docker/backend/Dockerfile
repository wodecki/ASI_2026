# ============================================================================
# Multi-stage build for minimal AutoGluon inference image
# Optimizations:
#   - CPU-only PyTorch on Linux (configured in pyproject.toml, saves several GB of CUDA libraries)
#   - Multi-stage build: build tools and uv cache stay in the builder stage
#   - Reproducible: installs exactly the versions pinned in uv.lock
#
# IMPORTANT: train the model first (uv run python "0. train.py").
# The image installs the same uv.lock you trained with - AutoGluon refuses to
# load a model saved by a different AutoGluon version.
# ============================================================================

# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12.21 /uv /usr/local/bin/uv

# Compile bytecode for faster startup; copy files instead of hard-linking from the cache;
# use the image's Python instead of downloading one
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Install dependencies first (cached layer), exactly as locked
COPY pyproject.toml uv.lock .python-version ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev --no-install-project

# --- Stage 2: Runtime (minimal) ---
FROM python:3.12-slim

# libgomp1: OpenMP runtime needed by LightGBM/torch; curl: health check
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the virtual environment from the builder (same path, so its scripts keep working)
COPY --from=builder /app/.venv /app/.venv

# Copy application code and model
COPY main.py ./
COPY data/ ./data/
COPY autogluon-iowa-daily/ ./autogluon-iowa-daily/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8003

EXPOSE 8003

# Health check (start period covers model loading)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8003/ || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
