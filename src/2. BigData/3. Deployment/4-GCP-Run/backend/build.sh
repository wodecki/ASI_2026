#!/bin/bash
# Build and push Docker image to GCP Artifact Registry

set -e

# Configuration - MODIFY THESE
PROJECT_ID="asi2025"
REGION="europe-west4"
REPOSITORY="iowa"
IMAGE_NAME="iowa-backend"
IMAGE_TAG="v1"

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
