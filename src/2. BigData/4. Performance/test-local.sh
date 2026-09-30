#!/bin/bash
# Load test against LOCAL Docker container
# Demonstrates: Single container = latency increases under load

set -e

echo "========================================="
echo "Load Test: LOCAL (No Auto-Scaling)"
echo "========================================="
echo ""
echo "IMPORTANT: Start Docker container FIRST!"
echo ""
echo "  cd ../3.\ Deployment/2-docker/backend"
echo "  docker run -d -p 8003:8003 --name iowa_backend iowa-backend:v1"
echo "  sleep 30  # Wait for model to load"
echo "  curl http://localhost:8003/items  # Verify it works"
echo ""
echo "Starting Locust..."
echo "Web UI: http://localhost:8089"
echo ""
echo "Locust Settings:"
echo "  - Number of users: 30-50 (simulated concurrent users)"
echo "  - Spawn rate: 5 (adds 5 users/second until reaching total)"
echo ""
echo "Expected Result:"
echo "  - Latency INCREASES with load (single container bottleneck)"
echo "  - Around 20+ users: response time >20-30s"
echo ""

uv run locust -f locustfile.py --host http://localhost:8003
