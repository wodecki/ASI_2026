#!/bin/bash
# Deploy FUNNY chatbot version to Cloud Run

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
: "${OPENAI_API_KEY:?Set OPENAI_API_KEY in .env}"
: "${OPENAI_MODEL:?Set OPENAI_MODEL in .env}"
IMAGE_NAME="chatbot-funny"
SERVICE_NAME="chatbot-funny"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Deploying FUNNY version to Cloud Run..."
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_URL}"
echo ""

# Deploy to Cloud Run with the API key and model name as environment variables
gcloud run deploy ${SERVICE_NAME} \
  --project ${PROJECT_ID} \
  --image ${IMAGE_URL} \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --port 8080 \
  --max-instances 5 \
  --set-env-vars "OPENAI_API_KEY=${OPENAI_API_KEY},OPENAI_MODEL=${OPENAI_MODEL}"

echo ""
echo "✓ FUNNY version deployed!"
echo ""
echo "Get service URL:"
echo "  gcloud run services describe ${SERVICE_NAME} --project ${PROJECT_ID} --region ${REGION} --format 'value(status.url)'"
echo ""
