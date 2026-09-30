# Backend - FastAPI

FastAPI backend serving AutoGluon time series predictions via REST API.

## Setup

```bash
# Install dependencies
uv sync

# Train the model (creates autogluon-iowa-daily/ directory)
uv run python "0. train.py"
```

## Run

```bash
# Start the server
uv run uvicorn main:app --host 0.0.0.0 --port 8003

# Or run directly
uv run python main.py
```

Server will be available at: http://localhost:8003

## API Endpoints

- `GET /` - Health check
- `GET /items` - List available products
- `GET /predict/{item_name}` - Get 7-day forecast for a product

## Test

```bash
# Health check
curl http://localhost:8003/

# Get predictions
curl http://localhost:8003/predict/BLACK%20VELVET
```
