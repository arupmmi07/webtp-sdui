#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🛑 Stopping all services..."

# Stop LiteLLM Docker containers
docker stop litellm-proxy litellm-db 2>/dev/null || true
docker rm litellm-proxy litellm-db 2>/dev/null || true
echo "✅ LiteLLM Proxy stopped" 2>/dev/null || true

# Stop API server
if [ -f "$PROJECT_DIR/logs/api.pid" ]; then
    PID=$(cat "$PROJECT_DIR/logs/api.pid")
    if kill -0 $PID 2>/dev/null; then
        kill $PID && echo "✅ API server stopped (PID: $PID)"
    else
        echo "⚠️  API server not running"
    fi
    rm "$PROJECT_DIR/logs/api.pid"
else
    echo "⚠️  No API server PID file found"
fi

# Stop Streamlit UI
if [ -f "$PROJECT_DIR/logs/ui.pid" ]; then
    PID=$(cat "$PROJECT_DIR/logs/ui.pid")
    if kill -0 $PID 2>/dev/null; then
        kill $PID && echo "✅ Streamlit UI stopped (PID: $PID)"
    else
        echo "⚠️  Streamlit UI not running"
    fi
    rm "$PROJECT_DIR/logs/ui.pid"
else
    echo "⚠️  No UI PID file found"
fi

echo ""
echo "✅ All services stopped"

