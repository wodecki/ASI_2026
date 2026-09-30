# Frontend - Streamlit (Docker)

Streamlit web interface containerized with Docker.

## Build & Run

```bash
# Build image
docker build -t iowa-frontend:v1 .

# Run container (make sure backend is running)
docker run -d --name iowa_frontend -p 8501:8501 -e API_URL=http://localhost:8003 iowa-frontend:v1
```

Frontend will be available at: http://localhost:8501

## Environment Variables

- `API_URL` - Backend API URL (default: `http://localhost:8003`)

## Usage

1. Ensure backend is running
2. Open http://localhost:8501 in your browser
3. Select a product and generate forecast
