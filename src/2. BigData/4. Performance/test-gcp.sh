#!/bin/bash
# Load test against GCP Cloud Run
# Demonstrates: Auto-scaling = stable latency under load

set -e

# Configuration - MODIFY THIS
GCP_URL="https://iowa-backend-850710718243.europe-west4.run.app"

echo "========================================="
echo "Load Test: GCP Cloud Run (Auto-Scaling)"
echo "========================================="
echo ""
echo "IMPORTANT: Verify GCP Run service is accessible!"
echo ""
echo "  curl ${GCP_URL}/items"
echo ""
echo "If service is not running, deploy it first:"
echo "  cd ../3.\ Deployment/3-GCP-Run/backend"
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
echo "  https://console.cloud.google.com/run/detail/europe-west4/iowa-backend-2/metrics"
echo ""

uv run locust -f locustfile.py --host ${GCP_URL}
