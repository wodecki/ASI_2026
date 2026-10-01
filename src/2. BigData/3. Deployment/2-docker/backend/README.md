# Backend - FastAPI (Docker)

FastAPI backend serving AutoGluon time series predictions via REST API, containerized with Docker.

## Train Model First

**IMPORTANT:** Train the model before building the Docker image.

```bash
# Install dependencies (including torch - see below)
uv sync

# Train the model
uv run python "0. train.py"
```

This creates the `autogluon-iowa-daily/` directory that the Dockerfile will copy.

### Note on PyTorch

`torch` is a regular dependency in `pyproject.toml` (`torch>=2.10,<2.11`, used by AutoGluon 1.6.3), so `uv sync` installs it - no manual `uv add` needed:
- **Linux (Docker image, GCP VM):** installed from the PyTorch CPU wheel index (`[tool.uv.sources]` + `[[tool.uv.index]] pytorch-cpu`), which avoids several GB of CUDA libraries
- **macOS:** installed from PyPI (standard wheels)

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

### CPU-Only PyTorch
`pyproject.toml` installs `torch` from the PyTorch CPU index on Linux:
```toml
[tool.uv.sources]
torch = [{ index = "pytorch-cpu", marker = "sys_platform == 'linux'" }]
```
- Removes CUDA libraries (not needed for inference)
- **Savings:** several GB

### Reproducible Dependencies
The Dockerfile copies `uv.lock` and runs `uv sync --locked`, so the container runs exactly
the versions you trained with locally. This matters: `TimeSeriesPredictor.load()` refuses to
load a model saved by a different AutoGluon version.

### Small Model Artifact
The saved model folder is tiny: the pretrained foundation model it uses (Toto2) is downloaded
from Hugging Face on the first prediction instead of being stored in `autogluon-iowa-daily/`.
The container therefore needs internet access at startup.

### Expected Image Size
- **Measured (September 2026, linux/arm64):** ~3.4 GB, of which the Python environment is ~2.3 GB
  (torch CPU ~0.6 GB, CatBoost ~0.27 GB, llvmlite, pyarrow, scipy, transformers)

### Verify Optimizations
```bash
# Check image size
docker images iowa-backend:v1

# Should be ~3.4GB

# Verify CPU-only PyTorch
docker run --rm iowa-backend:v1 python -c \
  "import torch; print(f'PyTorch: {torch.__version__}'); print(f'CUDA: {torch.cuda.is_available()}')"

# Expected output:
# PyTorch: 2.10.0+cpu
# CUDA: False
```

