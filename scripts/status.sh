#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📊 Service Status:"
echo ""

# Check API server
if [ -f "$PROJECT_DIR/logs/api.pid" ]; then
    PID=$(cat "$PROJECT_DIR/logs/api.pid")
    if kill -0 $PID 2>/dev/null; then
        echo "✅ API Server:    RUNNING (PID: $PID) - http://localhost:8000"
    else
        echo "❌ API Server:    STOPPED (stale PID file)"
    fi
else
    echo "❌ API Server:    STOPPED"
fi

# Check Streamlit UI
if [ -f "$PROJECT_DIR/logs/ui.pid" ]; then
    PID=$(cat "$PROJECT_DIR/logs/ui.pid")
    if kill -0 $PID 2>/dev/null; then
        echo "✅ Streamlit UI:  RUNNING (PID: $PID) - http://localhost:8501"
    else
        echo "❌ Streamlit UI:  STOPPED (stale PID file)"
    fi
else
    echo "❌ Streamlit UI:  STOPPED"
fi

