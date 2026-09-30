# ============================================================================
# Multi-stage build for minimal AutoGluon inference image
# Optimizations:
#   - CPU-only PyTorch (saves ~500MB)
#   - Multi-stage build (saves ~300MB)
#   - Minimal runtime dependencies
#   - Single-layer cleanup commands
# Expected final size: ~1.0-1.5GB (down from ~2.5GB)
# ============================================================================

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

# Copy pyproject.toml (without torch - we'll install CPU version separately)
COPY pyproject.toml ./

# Install CPU-only PyTorch first (saves ~500MB by avoiding CUDA)
RUN pip install --no-cache-dir --target=/install \
    torch==2.2.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu

# Install remaining dependencies via uv
RUN uv sync --no-dev

# --- Stage 2: Runtime (minimal) ---
FROM python:3.11-slim

# Install only essential runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

# Copy uv binary for running commands
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local/lib/python3.11/site-packages
COPY --from=builder /build/.venv /app/.venv

# Copy pyproject.toml for uv run to recognize dependencies
COPY pyproject.toml ./

# Copy application code and model
COPY main.py ./
COPY data/ ./data/
COPY autogluon-iowa-daily/ ./autogluon-iowa-daily/

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PORT=8003

EXPOSE 8003

# Health check (curl now installed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8003/ || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8003"]
