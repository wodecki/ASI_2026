#!/bin/bash
# Load test against GCP Cloud Run
# Demonstrates: Auto-scaling = stable latency under load

set -e

# Configuration is read from .env next to this script (copy .env.example to .env and fill it in)
cd "$(dirname "$0")"
if [ ! -f .env ]; then
    echo "ERROR: .env not found in $(pwd) - copy .env.example to .env and set the values" >&2
    exit 1
fi
set -a; source .env; set +a
: "${GCP_URL:?Set GCP_URL in .env}"
: "${PROJECT_ID:?Set PROJECT_ID in .env}"
: "${REGION:?Set REGION in .env}"
: "${SERVICE_NAME:?Set SERVICE_NAME in .env}"

echo "========================================="
echo "Load Test: GCP Cloud Run (Auto-Scaling)"
echo "========================================="
echo ""
echo "IMPORTANT: Verify GCP Run service is accessible!"
echo ""
echo "  curl ${GCP_URL}/items"
echo ""
echo "If service is not running, deploy it first:"
echo "  cd ../3.\ Deployment/4-GCP-Run/backend"
echo "  ./deploy.sh"
echo ""
echo "Starting Locust..."
echo "Web UI: http://localhost:8089"
echo ""
echo "The service must be deployed with --concurrency 1 and --max-instances 20"
echo "(deploy.sh does this; in the console: 'Maximum concurrent requests per instance' = 1)."
echo ""
echo "Locust Settings:"
echo "  - Number of users: 40-50 (simulated concurrent users)"
echo "  - Spawn rate: 2 (adds 2 users/second until reaching total)"
echo ""
echo "Expected Result:"
echo "  - First ~1 min: some slow responses (each NEW instance downloads model weights, ~30 s)"
echo "  - Then latency STAYS STABLE (~1-3 s) while users keep growing"
echo "  - Containers scale: 1 → 15-20 instances"
echo "  - RPS grows with users (~12-17 at 50 users)"
echo "  - More than ~60 users: all 20 instances busy → HTTP 429 failures"
echo ""
echo "Monitor auto-scaling (the console metrics lag ~3 minutes behind Locust):"
echo "  https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
echo ""

uv run locust -f locustfile.py --host ${GCP_URL}
