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
echo "Locust Settings:"
echo "  - Number of users: 80-100 (simulated concurrent users)"
echo "  - Spawn rate: 10 (adds 10 users/second until reaching total)"
echo ""
echo "Expected Result:"
echo "  - Latency STAYS STABLE (auto-scaling compensates)"
echo "  - Containers scale: 1 → 10-15 instances"
echo "  - RPS increases without latency degradation"
echo ""
echo "Monitor auto-scaling in real-time:"
echo "  https://console.cloud.google.com/run/detail/${REGION}/${SERVICE_NAME}/metrics?project=${PROJECT_ID}"
echo ""

uv run locust -f locustfile.py --host ${GCP_URL}
