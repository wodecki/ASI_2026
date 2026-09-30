# ============================================================================
# Optimized Streamlit frontend image
# Optimizations:
#   - Multi-stage build for minimal size
#   - Single-layer cleanup commands
#   - Minimal runtime dependencies
# ============================================================================

# --- Stage 1: Builder ---
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

# Copy and install dependencies
COPY pyproject.toml ./
RUN uv sync --no-dev

# --- Stage 2: Runtime (minimal) ---
FROM python:3.11-slim

# Clean up in single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /root/.cache

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /build/.venv /app/.venv

# Copy application code
COPY app.py ./

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["python", "-m", "streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
