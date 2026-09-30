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

| Optimization | Impact | Savings |
|-------------|---------|---------|
| **CPU-only PyTorch** | Removed CUDA dependencies | ~500MB |
| **Multi-stage build** | Separates build and runtime | ~300MB |
| **python:3.11-slim-buster** | Minimal base image | ~50MB |
| **Single-layer cleanup** | Removes build artifacts | ~100MB |
| **Deployment preset** | Optimizes model for inference | Faster loading |
| **Aggressive .dockerignore** | Excludes unnecessary files | ~50MB |

### Expected Results

| Configuration | Backend Size | Frontend Size |
|--------------|--------------|---------------|
| **Before optimization** | ~2.5GB | ~500MB |
| **After optimization** | ~1.0-1.5GB | ~300MB |
| **Savings** | **~40-60%** | **~40%** |

### Key Features

1. **CPU-only PyTorch**: Installed via `--index-url https://download.pytorch.org/whl/cpu`
2. **Multi-stage build**: Builder stage (with `uv` and build tools) + minimal runtime stage
3. **Built-in health checks**: Both containers include health checks for orchestration
4. **Optimized model**: Training uses `optimize_for_deployment` preset

### Verify Image Sizes

```bash
# Build images
docker compose build

# Check sizes
docker images | grep iowa

# Expected output:
# iowa-backend    ~1.2GB (down from ~2.5GB)
# iowa-frontend   ~300MB (down from ~500MB)
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
- Python 3.11 (for training)
- `uv` package manager
