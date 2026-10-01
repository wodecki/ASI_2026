#!/bin/bash
# Build and push Docker image to GCP Artifact Registry

set -e

# Configuration is read from .env next to this script (copy .env.example to .env and fill it in)
cd "$(dirname "$0")"
if [ ! -f .env ]; then
    echo "ERROR: .env not found in $(pwd) - copy .env.example to .env and set the values" >&2
    exit 1
fi
set -a; source .env; set +a
: "${PROJECT_ID:?Set PROJECT_ID in .env}"
: "${REGION:?Set REGION in .env}"
: "${REPOSITORY:?Set REPOSITORY in .env}"
: "${IMAGE_TAG:?Set IMAGE_TAG in .env}"
IMAGE_NAME="iowa-backend"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building image: ${IMAGE_URL}"
echo ""

# Check model exists
if [ ! -d "autogluon-iowa-daily" ]; then
    echo "ERROR: Train model first with: uv run python '0. train.py'"
    exit 1
fi

# 1. Build image for linux/amd64 (Cloud Run requirement)
echo "Building Docker image..."
docker build --platform linux/amd64 -t ${IMAGE_NAME}:${IMAGE_TAG} .

# 2. Tag for Artifact Registry
echo "Tagging image..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_URL}

# 3. Configure authentication
echo "Configuring authentication..."
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# 4. Push to Artifact Registry
echo "Pushing to Artifact Registry (this may take 5-10 minutes)..."
docker push ${IMAGE_URL}

echo ""
echo "✓ Image pushed successfully!"
echo ""
echo "Image URL: ${IMAGE_URL}"
echo ""
echo "Next: Deploy to Cloud Run with ./deploy.sh"
echo ""
