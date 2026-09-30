#!/bin/bash
# Build and push SERIOUS chatbot version

set -e

# Configuration
PROJECT_ID="asi2025"
REGION="europe-west4"
REPOSITORY="chatbot"
IMAGE_NAME="chatbot-serious"
IMAGE_TAG="v1"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building SERIOUS version..."
echo "Image: ${IMAGE_URL}"
echo ""

# Build for linux/amd64 (Cloud Run requirement)
docker build --platform linux/amd64 -f Dockerfile-serious -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Tag for Artifact Registry
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_URL}

# Configure authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Push to Artifact Registry
echo "Pushing to Artifact Registry..."
docker push ${IMAGE_URL}

echo ""
echo "✓ SERIOUS version pushed!"
echo "Image URL: ${IMAGE_URL}"
echo ""
echo "Next: Deploy with ./deploy-serious.sh"
echo ""
