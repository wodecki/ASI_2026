#!/bin/bash
# Deploy SERIOUS chatbot version to Cloud Run

set -e

# Configuration
PROJECT_ID="asi2025"
REGION="europe-west4"
REPOSITORY="chatbot"
IMAGE_NAME="chatbot-serious"
IMAGE_TAG="v1"
SERVICE_NAME="chatbot-serious"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Deploying SERIOUS version to Cloud Run..."
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_URL}"
echo ""

# Check if OPENAI_API_KEY is set locally (for deployment)
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY not set!"
    echo "Please export it first:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

# Deploy to Cloud Run with API key as environment variable
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --port 8080 \
  --max-instances 5 \
  --set-env-vars OPENAI_API_KEY=${OPENAI_API_KEY}

echo ""
echo "✓ SERIOUS version deployed!"
echo ""
echo "Get service URL:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'"
echo ""
