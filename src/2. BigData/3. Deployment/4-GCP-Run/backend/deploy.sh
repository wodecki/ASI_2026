#!/bin/bash
# Deploy to GCP Cloud Run

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
: "${SERVICE_NAME:?Set SERVICE_NAME in .env}"
IMAGE_NAME="iowa-backend"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Deploying to Cloud Run..."
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_URL}"
echo ""

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --project ${PROJECT_ID} \
  --image ${IMAGE_URL} \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8080 \
  --max-instances 10

echo ""
echo "✓ Deployment complete!"
echo ""
echo "Get service URL with:"
echo "  gcloud run services describe ${SERVICE_NAME} --project ${PROJECT_ID} --region ${REGION} --format 'value(status.url)'"
echo ""
