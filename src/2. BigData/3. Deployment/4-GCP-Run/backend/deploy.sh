#!/bin/bash
# Deploy to GCP Cloud Run

set -e

# Configuration - MODIFY THESE
PROJECT_ID="asi2025"
REGION="europe-west4"
REPOSITORY="iowa"
IMAGE_NAME="iowa-backend"
IMAGE_TAG="v1"
SERVICE_NAME="iowa-backend-2"

IMAGE_URL="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "Deploying to Cloud Run..."
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_URL}"
echo ""

# Deploy to Cloud Run
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_URL} \
  --platform managed \
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
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'"
echo ""
