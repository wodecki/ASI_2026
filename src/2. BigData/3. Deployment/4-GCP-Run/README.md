# GCP Cloud Run Deployment

Deploy the Iowa Sales API to **Google Cloud Run** - a serverless container platform.

## Quick Start

```bash
cd backend

# Train model
uv sync
uv run python "0. train.py"

# Configure scripts (edit PROJECT_ID, REGION)
nano build.sh deploy.sh

# Build and push to Artifact Registry
./build.sh

# Deploy to Cloud Run
./deploy.sh
```

## What's Inside

```
3-GCP-Run/
├── README.md              # This file
└── backend/
    ├── README.md          # Complete deployment guide
    ├── build.sh           # Build & push to registry
    ├── deploy.sh          # Deploy to Cloud Run
    ├── Dockerfile         # Cloud Run optimized
    ├── main.py            # FastAPI app
    └── 0. train.py        # Model training
```

## Why Cloud Run?

- **Serverless**: No servers to manage
- **Auto-scaling**: 0 → 1000+ instances automatically
- **Cheap**: ~$1-2/month for demo usage
- **HTTPS**: Automatic SSL certificates
- **Global**: Deploy to 20+ regions worldwide

## Prerequisites

1. GCP account with billing
2. gcloud CLI installed (`brew install --cask google-cloud-sdk`)
3. Docker running
4. Model trained

## Full Documentation

See **[backend/README.md](backend/README.md)** for:
- Detailed setup instructions
- GCP project configuration
- Deployment walkthrough
- Testing & troubleshooting
- Cost breakdown

## Key Differences from Docker

| | Local Docker | Cloud Run |
|---|---|---|
| **Platform** | linux/arm64 or amd64 | linux/amd64 only |
| **Port** | 8003 | 8080 |
| **Scaling** | Manual | Automatic |
| **Cost** | Free | ~$1-2/month |
| **URL** | localhost | HTTPS public URL |

## Testing

After deployment:
```bash
# Replace with your actual URL
curl https://iowa-sales-api-abc123-uc.a.run.app/
curl https://iowa-sales-api-abc123-uc.a.run.app/predict/BLACK%20VELVET
```

## Resources

- Cloud Run docs: https://cloud.google.com/run/docs
- Pricing: https://cloud.google.com/run/pricing
