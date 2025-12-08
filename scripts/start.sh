#!/bin/bash
set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🚀 Starting Healthcare Operations Assistant..."
echo ""

# Kill any process on port 8000
echo "🔍 Checking port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null && echo "✅ Killed existing process on port 8000" || echo "✅ Port 8000 is free"
echo ""

# Ensure logs directory exists
mkdir -p "$PROJECT_DIR/logs"

# Export LiteLLM environment variables
# Option 1: Direct to LM Studio (faster, no logs)
# export LITELLM_BASE_URL="http://localhost:1234/v1"
# export LITELLM_API_KEY="lm-studio"

# Option 2: Through LiteLLM Proxy (slower, but shows logs for demo)
export LITELLM_BASE_URL="http://localhost:4000"
export LITELLM_API_KEY="sk-1234"

export LITELLM_DEFAULT_MODEL="openai/gpt-oss-20b"
export USE_MOCK_LLM="false"

echo "🤖 LLM Configuration:"
echo "   Provider: LiteLLM Proxy → LM Studio"
echo "   Model: ${LITELLM_DEFAULT_MODEL}"
echo "   API: ${LITELLM_BASE_URL}"
echo "   💡 Traffic routed through proxy for demo monitoring"
echo ""

# Start LiteLLM proxy in Docker for demo UI
echo "🐳 Starting LiteLLM Proxy (Demo UI)..."
docker rm -f litellm-proxy litellm-db 2>/dev/null || true

# Start PostgreSQL for LiteLLM
docker run -d \
  --name litellm-db \
  -e POSTGRES_USER=litellm \
  -e POSTGRES_PASSWORD=litellm123 \
  -e POSTGRES_DB=litellm \
  -p 5433:5432 \
  postgres:15-alpine > /dev/null 2>&1

# Wait for DB to be ready
sleep 3

# Start LiteLLM proxy with DB
docker run -d \
  --name litellm-proxy \
  --link litellm-db:db \
  -p 4000:4000 \
  -v "$PROJECT_DIR/config/litellm_config.yaml:/app/config.yaml" \
  -e LITELLM_MASTER_KEY=sk-1234 \
  -e LITELLM_SALT_KEY=sk-salt-1234567890 \
  -e DATABASE_URL=postgresql://litellm:litellm123@db:5432/litellm \
  -e STORE_MODEL_IN_DB=True \
  ghcr.io/berriai/litellm:main-latest \
  --config /app/config.yaml --port 4000 --detailed_debug > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ LiteLLM Proxy started"
    echo "   UI: http://localhost:4000/ui (admin/sk-1234)"
else
    echo "⚠️  LiteLLM Proxy failed to start (Docker may not be running)"
fi
echo ""

# Check for port conflicts and clean up
echo "🔍 Checking for port conflicts..."
API_PORT_IN_USE=$(lsof -ti:8000 || echo "")
UI_PORT_IN_USE=$(lsof -ti:8501 || echo "")

if [ ! -z "$API_PORT_IN_USE" ]; then
    echo "⚠️  Port 8000 already in use (PID: $API_PORT_IN_USE)"
    echo "   Killing existing process..."
    kill -9 $API_PORT_IN_USE 2>/dev/null || true
    sleep 1
fi

if [ ! -z "$UI_PORT_IN_USE" ]; then
    echo "⚠️  Port 8501 already in use (PID: $UI_PORT_IN_USE)"
    echo "   Killing existing process..."
    kill -9 $UI_PORT_IN_USE 2>/dev/null || true
    sleep 1
fi

# Clean up old PID files
rm -f "$PROJECT_DIR/logs/api.pid" "$PROJECT_DIR/logs/ui.pid"

echo "✅ Ports cleared"
echo ""

# Source virtual environment
source "$PROJECT_DIR/venv/bin/activate"

# Start API server
echo "Starting API server..."
cd "$PROJECT_DIR"
python api/server.py > "$PROJECT_DIR/logs/api.log" 2>&1 &
API_PID=$!
echo $API_PID > "$PROJECT_DIR/logs/api.pid"
sleep 3

if kill -0 $API_PID 2>/dev/null; then
    echo "✅ API server started (PID: $API_PID)"
    echo "   URL: http://localhost:8000"
    echo "   Logs: logs/api.log"
else
    echo "❌ Failed to start API server"
    cat "$PROJECT_DIR/logs/api.log"
    exit 1
fi

echo ""

# Start Streamlit UI
echo "Starting Streamlit UI..."
cd "$PROJECT_DIR/demo"
streamlit run chat_ui.py --server.headless true > "$PROJECT_DIR/logs/ui.log" 2>&1 &
UI_PID=$!
echo $UI_PID > "$PROJECT_DIR/logs/ui.pid"
sleep 3

if kill -0 $UI_PID 2>/dev/null; then
    echo "✅ Streamlit UI started (PID: $UI_PID)"
    echo "   URL: http://localhost:8501"
    echo "   Logs: logs/ui.log"
else
    echo "❌ Failed to start Streamlit UI"
    cat "$PROJECT_DIR/logs/ui.log"
    # Clean up API server
    kill $API_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ All services running!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📱 Application URLs:"
echo "   • Chat UI:    http://localhost:8501/"
echo "   • Calendar:   http://localhost:8000/schedule.html"
echo "   • Emails:     http://localhost:8000/emails.html"
echo "   • API Docs:   http://localhost:8000/docs"
echo ""
echo "🎨 LiteLLM Demo UI:"
echo "   • URL:        http://localhost:4000/ui"
echo "   • Login:      admin / sk-1234"
echo "   • Features:   Model dashboard, real-time monitoring, cost tracking"
echo ""
echo "🤖 LLM: LM Studio (http://localhost:1234)"
echo "   Model: ${LITELLM_DEFAULT_MODEL}"
echo ""
echo "📋 Commands:"
echo "   • View logs:  make logs"
echo "   • Stop all:   make stop"
echo ""

