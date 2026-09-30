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

# Or with custom API URL
API_URL=http://localhost:8003 uv run streamlit run app.py
```

Frontend will be available at: http://localhost:8501

## Usage

1. Make sure the backend is running at http://localhost:8003
2. Open the frontend in your browser
3. Select a product from the dropdown
4. Click "Generate Forecast" to see predictions
