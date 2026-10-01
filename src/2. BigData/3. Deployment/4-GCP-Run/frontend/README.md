# Frontend - Streamlit

Streamlit web interface for viewing sales forecasts from the FastAPI backend.

## Setup

```bash
# Install dependencies
uv sync
```

## Run

```bash
# Start the frontend
uv run streamlit run app.py

# Or point it at your Cloud Run backend (the service URL printed by deploy.sh)
API_URL=https://iowa-backend-XXXXXXXXXX.europe-west4.run.app uv run streamlit run app.py
```

Frontend will be available at: http://localhost:8501

## Usage

1. Make sure the backend is running on your Cloud Run service, e.g. `https://iowa-backend-XXXXXXXXXX.europe-west4.run.app` (the URL printed by `backend/deploy.sh`; without `API_URL` the frontend uses `http://localhost:8003`)
2. Open the frontend in your browser
3. Select a product from the dropdown
4. Click "Generate Forecast" to see predictions
