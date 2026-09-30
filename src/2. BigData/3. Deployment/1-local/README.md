# Local Deployment

FastAPI backend and Streamlit frontend running locally for Iowa alcohol sales forecasting.

## Architecture

```
User Browser (localhost:8501)
         ↓
Streamlit Frontend
         ↓ HTTP
FastAPI Backend (localhost:8003)
         ↓
AutoGluon Model
```

## Quick Start

### 1. Train Model (Terminal 1)

```bash
cd backend/
uv sync
uv run python "0. train.py"
```

### 2. Start Backend (Terminal 1)

```bash
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8003
```

Backend will be available at: http://localhost:8003

### 3. Start Frontend (Terminal 2)

```bash
cd frontend/
uv sync
uv run streamlit run app.py
```

Frontend will be available at: http://localhost:8501

## Test

**Backend API:**
```bash
curl http://localhost:8003/
curl http://localhost:8003/predict/BLACK%20VELVET
```

**Frontend:**
Open http://localhost:8501 in your browser and select a product.

## Files

- `backend/0. train.py` - Train the AutoGluon model
- `backend/main.py` - FastAPI backend server
- `frontend/app.py` - Streamlit frontend UI

## Requirements

- Python 3.10 or 3.11
- `uv` package manager
