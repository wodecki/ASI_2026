# Backend - FastAPI (Docker)

FastAPI backend serving AutoGluon time series predictions via REST API, containerized with Docker.

## Train Model First

**IMPORTANT:** Train the model before building the Docker image.

```bash
# Install dependencies (note: torch not in pyproject.toml - see below)
uv sync

# For local training, you may need to add torch manually:
uv add "torch>=2.2.0,<2.3.0"

# Train the model
uv run python "0. train.py"
```

This creates the `autogluon-iowa-daily/` directory that the Dockerfile will copy.

### Note on PyTorch

The `pyproject.toml` does **not** include `torch` as a dependency because:
- **Docker:** Uses CPU-only PyTorch (installed in Dockerfile) for smaller images (~500MB savings)
- **Local dev:** You may need full PyTorch with GPU support

For local development, install torch manually:
```bash
uv add "torch>=2.2.0,<2.3.0"
```

## Build & Run

```bash
# Build image
docker build -t iowa-backend:v1 .

# Run container
docker run -d --name iowa_backend -p 8003:8003 iowa-backend:v1
```

Backend will be available at: http://localhost:8003

## API Endpoints

- `GET /` - Health check
- `GET /items` - List available products
- `GET /predict/{item_name}` - Get 7-day forecast

## Test

```bash
curl http://localhost:8003/
curl http://localhost:8003/predict/BLACK%20VELVET
```

## Docker Image Optimizations

This Dockerfile uses several optimization strategies to minimize image size:

### Multi-Stage Build
- **Builder stage:** Installs dependencies with build tools
- **Runtime stage:** Only copies necessary files (no build tools)
- **Savings:** ~300MB

### CPU-Only PyTorch
```dockerfile
RUN pip install --no-cache-dir --target=/install \
    torch==2.2.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu
```
- Removes CUDA libraries (not needed for inference)
- **Savings:** ~500MB

### Deployment-Optimized Model
The training script uses `optimize_for_deployment` preset:
```python
predictor.fit(..., presets=["medium_quality", "optimize_for_deployment"])
```
- Removes intermediate models
- Compresses weights
- Faster loading

### Expected Image Size
- **Before optimization:** ~2.5GB
- **After optimization:** ~1.0-1.5GB
- **Reduction:** ~40-60%

### Verify Optimizations
```bash
# Check image size
docker images iowa-backend:v1

# Should be ~1.2GB (down from ~2.5GB)

# Verify CPU-only PyTorch
docker run --rm iowa-backend:v1 python -c \
  "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# Expected output:
# PyTorch: 2.2.0+cpu
# CUDA: False
```

See `../OPTIMIZATION_GUIDE.md` for detailed technical explanation.
