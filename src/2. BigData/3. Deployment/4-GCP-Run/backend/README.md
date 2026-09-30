# GCP Cloud Run Deployment - Backend

Deploy the Iowa Sales forecasting API to **Google Cloud Run** - a serverless platform for containerized applications.

## What is Cloud Run?

Cloud Run runs Docker containers without managing servers:
- **Serverless**: No infrastructure to manage
- **Auto-scaling**: Scales from 0 → N instances automatically
- **Pay-per-use**: Only charged during request handling
- **HTTPS**: Automatic SSL certificates
- **Cost**: ~$1-2/month for typical demo usage

## Prerequisites

1. **GCP Account** with billing enabled
2. **gcloud CLI** installed and authenticated
3. **Docker** running
4. **Model trained** (run `0. train.py`)

### Install gcloud CLI

**macOS:**
```bash
brew install --cask google-cloud-sdk
```

**Linux/Windows:** https://cloud.google.com/sdk/docs/install

### Setup GCP

```bash
# Login
gcloud auth login

# Set project
gcloud config set project asi2025

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry repository (REQUIRED - build.sh will fail without this)
gcloud artifacts repositories create iowa-sales \
  --repository-format=docker \
  --location=us-central1 \
  --description="Iowa sales containers"

# Verify repository was created
gcloud artifacts repositories list
```

### Train Model

```bash
cd backend
uv sync
uv run python "0. train.py"
```

This creates `autogluon-iowa-daily/` directory needed for deployment.

## Deployment Steps

### 1. Configure Scripts

Edit `build.sh` and `deploy.sh` with your values:
```bash
PROJECT_ID="asi2025"           # Your GCP project
REGION="europe-west4"           # Deployment region
REPOSITORY="iowa-sales"        # Registry repo name
IMAGE_NAME="iowa-backend"
IMAGE_TAG="v1"
SERVICE_NAME="iowa-sales-api"
```

### 2. Build and Push Image

```bash
./build.sh
```

This script:
1. Builds Docker image for `linux/amd64`
2. Tags for Artifact Registry
3. Configures authentication
4. Pushes image (~5-10 minutes)

### 3. Deploy to Cloud Run

```bash
./deploy.sh
```

This script deploys the image to Cloud Run with:
- `--memory 2Gi` - AutoGluon needs RAM
- `--cpu 2` - Faster predictions
- `--allow-unauthenticated` - Public access (no auth)
- `--max-instances 10` - Cost control

You'll get a URL like:
```
https://iowa-sales-api-abc123-uc.a.run.app
```

### 4. Test

```bash
# Health check
curl https://iowa-sales-api-abc123-uc.a.run.app/

# Prediction
curl https://iowa-sales-api-abc123-uc.a.run.app/predict/BLACK%20VELVET

# Interactive docs
open https://iowa-sales-api-abc123-uc.a.run.app/docs
```

## Cost Estimate

**Free tier** (per month):
- 2M requests
- 360K vCPU-seconds
- 180K GiB-seconds memory

**Example** (10K requests/month, 2s avg response):
- Compute: ~$1.06
- Storage: ~$0.15
- **Total: ~$1.21/month**

## Troubleshooting

**build.sh fails with "Repository not found":**
```bash
# Create the repository first
gcloud artifacts repositories create iowa-sales \
  --repository-format=docker \
  --location=us-central1 \
  --description="Iowa sales containers"

# Verify it exists
gcloud artifacts repositories list
```

**Container fails to start:**
```bash
gcloud run services logs read iowa-sales-api --region us-central1 --limit 20
```

Common issues:
- Missing `autogluon-iowa-daily/` → Train model first
- Out of memory → Increase to `--memory 4Gi`
- Cold start slow → Set `--min-instances 1`

**Update deployment:**
```bash
# Change IMAGE_TAG to v2 in build.sh and deploy.sh, then:
./build.sh
./deploy.sh
```

## Clean Up

```bash
# Delete service
gcloud run services delete iowa-sales-api --region us-central1

# Delete image
gcloud artifacts docker images delete \
  us-central1-docker.pkg.dev/asi2025/iowa-sales/iowa-backend:v1
```

## Key Differences from Docker

| Feature | Local Docker | Cloud Run |
|---------|--------------|-----------|
| Hosting | Your machine | Google cloud |
| Scaling | Manual | Automatic |
| Cost | Free | ~$1-2/month |
| URL | localhost:8003 | HTTPS with SSL |
| Availability | When PC is on | 99.95% SLA |

## Resources

- Cloud Run docs: https://cloud.google.com/run/docs
- Pricing calculator: https://cloud.google.com/products/calculator
- Quotas: https://cloud.google.com/run/quotas
