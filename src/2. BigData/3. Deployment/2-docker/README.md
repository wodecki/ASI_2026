# Docker Deployment

Multi-container deployment using Docker and Docker Compose for Iowa alcohol sales forecasting.

## Architecture

```
User Browser (localhost:8501)
         ↓
Streamlit Container (iowa_frontend)
         ↓ HTTP (Docker network)
FastAPI Container (iowa_backend)
         ↓
AutoGluon Model
```

## Quick Start (Docker Compose)

### 1. Train Model

```bash
cd backend/
uv sync
uv run python "0. train.py"
```

### 2. Build and Run

```bash
cd ..
docker compose up --build
```

Services:
- Backend: http://localhost:8003
- Frontend: http://localhost:8501

### 3. Stop

```bash
docker compose down
```

## Docker Image Optimizations

This deployment uses **optimized Docker images** for minimal size and faster deployment:

### Optimization Strategies Applied

| Optimization | Impact |
|-------------|---------|
| **CPU-only PyTorch** | No CUDA libraries (the CUDA build of torch adds several GB) |
| **Multi-stage build** | uv, its cache and build files stay in the builder stage |
| **python:3.12-slim** | Minimal Debian base image |
| **Aggressive .dockerignore** | Excludes unnecessary files from the build context |

### Measured Image Sizes

Measured in September 2026 (Docker Desktop, linux/arm64, `docker images`):

| Image | Size | Notes |
|-------|------|-------|
| **Backend** | ~3.4 GB | Python environment ~2.3 GB: torch (CPU) ~0.6 GB, CatBoost ~0.27 GB, llvmlite, pyarrow, scipy, transformers |
| **Frontend** | ~0.8 GB | Streamlit, pandas, pyarrow |

AutoGluon 1.6 depends on more libraries than earlier versions (e.g. `transformers` for the
foundation models), so the backend image is larger than in previous course editions.

### Key Features

1. **CPU-only PyTorch**: On Linux, `pyproject.toml` points `torch` at the `https://download.pytorch.org/whl/cpu` index
2. **Multi-stage build**: Builder stage (with `uv` and build tools) + minimal runtime stage
3. **Built-in health checks**: Both containers include health checks for orchestration
4. **Reproducible installs**: The image copies `uv.lock` and runs `uv sync --locked`, so it runs exactly the library versions the model was trained with (AutoGluon refuses to load a model saved by a different AutoGluon version)

### Verify Image Sizes

```bash
# Build images
docker compose build

# Check sizes (compose names the images after the folder)
docker images | grep 2-docker

# Expected output (approximately):
# 2-docker-backend    3.4GB
# 2-docker-frontend   0.8GB
```

### Compare with Previous Version

To compare with non-optimized images, you can build a baseline version:

```bash
# Build optimized (current)
docker compose build
docker images | grep iowa

# The optimized images use:
# - Multi-stage builds
# - CPU-only PyTorch
# - Minimal base images
```

## Manual Docker Commands

### Build Images

```bash
cd backend/
docker build -t iowa-backend:v1 .

cd ../frontend/
docker build -t iowa-frontend:v1 .
```

### Create Network

```bash
docker network create iowa-network
```

### Run Containers

```bash
# Backend
docker run -d \
  --name iowa_backend \
  --network iowa-network \
  -p 8003:8003 \
  iowa-backend:v1

# Frontend
docker run -d \
  --name iowa_frontend \
  --network iowa-network \
  -p 8501:8501 \
  -e API_URL=http://iowa_backend:8003 \
  iowa-frontend:v1
```

### Cleanup

```bash
docker stop iowa_frontend iowa_backend
docker rm iowa_frontend iowa_backend
docker network rm iowa-network
```

## Test

```bash
# Backend API
curl http://localhost:8003/
curl http://localhost:8003/predict/BLACK%20VELVET

# Frontend
open http://localhost:8501
```

## Requirements

- Docker Desktop
- Python 3.12 (for training; installed automatically by uv)
- `uv` package manager
