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

# Set project (replace with your project ID)
gcloud config set project your-gcp-project-id

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry repository (REQUIRED - build.sh will fail without this)
# Name and location must match REPOSITORY and REGION in .env
gcloud artifacts repositories create iowa \
  --repository-format=docker \
  --location=europe-west4 \
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

### 1. Configure `.env`

`build.sh` and `deploy.sh` read their settings from a `.env` file in `backend/` (next to the scripts) - you do not edit the scripts. Create it from the template and fill it in:
```bash
cp .env.example .env
```

```bash
# .env
PROJECT_ID=your-gcp-project-id   # Your GCP project ID (see: gcloud projects list)
REGION=europe-west4              # Deployment region
REPOSITORY=iowa                  # Artifact Registry repository name
IMAGE_TAG=v1
SERVICE_NAME=iowa-backend        # Cloud Run service name
```

Both scripts stop with an error if `.env` is missing or any of these values is empty. The image name is fixed to `iowa-backend`, so the image URL is `${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/iowa-backend:${IMAGE_TAG}`, e.g. `europe-west4-docker.pkg.dev/your-gcp-project-id/iowa/iowa-backend:v1`.

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

Get the service URL (the command is also printed at the end of `deploy.sh`):
```bash
gcloud run services describe iowa-backend --project your-gcp-project-id --region europe-west4 --format 'value(status.url)'
```

It looks like:
```
https://iowa-backend-XXXXXXXXXX.europe-west4.run.app
```

### 4. Test

```bash
# Health check
curl https://iowa-backend-XXXXXXXXXX.europe-west4.run.app/

# Prediction
curl https://iowa-backend-XXXXXXXXXX.europe-west4.run.app/predict/BLACK%20VELVET

# Interactive docs
open https://iowa-backend-XXXXXXXXXX.europe-west4.run.app/docs
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
# Create the repository first (must match REPOSITORY and REGION in .env)
gcloud artifacts repositories create iowa \
  --repository-format=docker \
  --location=europe-west4 \
  --description="Iowa sales containers"

# Verify it exists
gcloud artifacts repositories list
```

**Container fails to start:**
```bash
gcloud run services logs read iowa-backend --project your-gcp-project-id --region europe-west4 --limit 20
```

Common issues:
- Missing `autogluon-iowa-daily/` → Train model first
- Out of memory → Increase to `--memory 4Gi`
- Cold start slow → Set `--min-instances 1`

**Update deployment:**
```bash
# Change IMAGE_TAG to v2 in .env, then:
./build.sh
./deploy.sh
```

## Clean Up

```bash
# Delete service
gcloud run services delete iowa-backend --project your-gcp-project-id --region europe-west4

# Delete image
gcloud artifacts docker images delete \
  europe-west4-docker.pkg.dev/your-gcp-project-id/iowa/iowa-backend:v1
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
