#!/bin/bash
# Simple deployment script for GCP VMs

set -e

echo "🚀 Deploying WebTP Demo..."

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables (edit these)
export APP_BASE_URL="http://$(hostname -I | awk '{print $1}'):8000"
export AZURE_API_KEY="${AZURE_API_KEY}"
export AZURE_API_BASE="${AZURE_API_BASE}"
export AZURE_DEPLOYMENT_NAME="${AZURE_DEPLOYMENT_NAME}"

# Start API server
echo "Starting API server on port 8000..."
nohup python api/server.py > logs/api.log 2>&1 &

echo "✅ Deployed! Access at: ${APP_BASE_URL}/schedule.html"

