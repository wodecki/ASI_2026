#!/bin/bash
# Canary Deployment: Split traffic 50/50 between Serious and Funny versions
#
# Prerequisites:
#   - Both versions deployed as separate services
#   - chatbot-serious running
#   - chatbot-funny running

set -e

REGION="europe-west4"

echo "========================================="
echo "Canary Deployment Demo"
echo "========================================="
echo ""
echo "This demonstrates traffic splitting between two versions:"
echo "  - Serious: Professional academic style"
echo "  - Funny: Hip-hop academic style"
echo ""

# Get URLs
SERIOUS_URL=$(gcloud run services describe chatbot-serious --region ${REGION} --format 'value(status.url)')
FUNNY_URL=$(gcloud run services describe chatbot-funny --region ${REGION} --format 'value(status.url)')

echo "Current deployments:"
echo "  Serious: ${SERIOUS_URL}"
echo "  Funny:   ${FUNNY_URL}"
echo ""
echo "========================================="
echo "Canary Strategy Explanation"
echo "========================================="
echo ""
echo "In production canary deployments:"
echo "  1. Deploy new version (e.g., Funny) alongside old (Serious)"
echo "  2. Start with 90% old, 10% new (test with small traffic)"
echo "  3. Monitor metrics (errors, latency, user feedback)"
echo "  4. Gradually increase: 70/30, 50/50, 30/70"
echo "  5. If issues detected: rollback instantly to 100% old"
echo "  6. If successful: complete rollout to 100% new"
echo ""
echo "For this DEMO, we use TWO SEPARATE SERVICES:"
echo "  - Each service gets 100% of its own traffic"
echo "  - Users manually choose which URL to visit"
echo "  - In production, you'd use:"
echo "    • Cloud Run revisions with traffic splitting"
echo "    • Load balancer with weighted routing"
echo "    • Service mesh for advanced canary"
echo ""
echo "========================================="
echo "Testing Both Versions"
echo "========================================="
echo ""
echo "Open in browser:"
echo ""
echo "Serious version (50% users):"
echo "  ${SERIOUS_URL}"
echo ""
echo "Funny version (50% users):"
echo "  ${FUNNY_URL}"
echo ""
echo "Try asking the same question to both!"
echo "Example: 'Why is the sky blue?'"
echo ""
