#!/bin/bash
# Build and push FUNNY chatbot version

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
IMAGE_NAME="chatbot-funny"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building FUNNY version..."
echo "Image: ${IMAGE_URL}"
echo ""

# Build for linux/amd64 (Cloud Run requirement)
docker build --platform linux/amd64 -f Dockerfile-funny -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Tag for Artifact Registry
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${IMAGE_URL}

# Configure authentication
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Push to Artifact Registry
echo "Pushing to Artifact Registry..."
docker push ${IMAGE_URL}

echo ""
echo "✓ FUNNY version pushed!"
echo "Image URL: ${IMAGE_URL}"
echo ""
echo "Next: Deploy with ./deploy-funny.sh"
echo ""
