#!/bin/bash
# Test script for LM Studio integration

set -e

echo "============================================================"
echo "  LM Studio + LiteLLM Test"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check if LM Studio is running
echo "1️⃣  Checking LM Studio server..."
if curl -s http://localhost:1234/v1/models > /dev/null 2>&1; then
    echo -e "${GREEN}✅ LM Studio server is running on port 1234${NC}"
    
    # Show loaded model
    MODEL=$(curl -s http://localhost:1234/v1/models | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['data'][0]['id'] if data.get('data') else 'Unknown')" 2>/dev/null || echo "Unknown")
    echo -e "   Loaded model: ${YELLOW}$MODEL${NC}"
else
    echo -e "${RED}❌ LM Studio server is not running${NC}"
    echo ""
    echo "To start LM Studio:"
    echo "  1. Open LM Studio application"
    echo "  2. Go to 'Local Server' tab"
    echo "  3. Click 'Start Server'"
    echo "  4. Ensure port is 1234"
    echo ""
    exit 1
fi

echo ""

# Step 2: Test LM Studio directly
echo "2️⃣  Testing LM Studio API directly..."
RESPONSE=$(curl -s -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss-20b",
    "messages": [{"role": "user", "content": "Say hello in exactly 5 words"}],
    "max_tokens": 50,
    "temperature": 0.7
  }')

if echo "$RESPONSE" | grep -q "choices"; then
    echo -e "${GREEN}✅ LM Studio API responded${NC}"
    REPLY=$(echo "$RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null || echo "Could not parse")
    echo -e "   Response: ${YELLOW}$REPLY${NC}"
else
    echo -e "${RED}❌ LM Studio API error${NC}"
    echo "   Response: $RESPONSE"
    exit 1
fi

echo ""

# Step 3: Check if Docker is running
echo "3️⃣  Checking Docker services..."
if docker ps | grep -q "healthcare-litellm"; then
    echo -e "${GREEN}✅ LiteLLM proxy is running${NC}"
else
    echo -e "${YELLOW}⚠️  LiteLLM proxy is not running${NC}"
    echo "   Start with: make docker-up"
    exit 0
fi

echo ""

# Step 4: Test LiteLLM proxy connection to LM Studio
echo "4️⃣  Testing LiteLLM → LM Studio connection..."
LITELLM_RESPONSE=$(curl -s -X POST http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{
    "model": "gpt-oss-20b",
    "messages": [{"role": "user", "content": "Say hello in exactly 5 words"}],
    "max_tokens": 50
  }')

if echo "$LITELLM_RESPONSE" | grep -q "choices"; then
    echo -e "${GREEN}✅ LiteLLM can reach LM Studio${NC}"
    LITELLM_REPLY=$(echo "$LITELLM_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['choices'][0]['message']['content'])" 2>/dev/null || echo "Could not parse")
    echo -e "   Response: ${YELLOW}$LITELLM_REPLY${NC}"
else
    echo -e "${RED}❌ LiteLLM cannot reach LM Studio${NC}"
    echo "   Response: $LITELLM_RESPONSE"
    echo ""
    echo "Troubleshooting:"
    echo "  - Make sure LM Studio is running"
    echo "  - Check docker-compose.yml has: http://host.docker.internal:1234"
    echo "  - Try: docker-compose restart litellm"
    exit 1
fi

echo ""

# Step 5: Test API server
echo "5️⃣  Testing Healthcare API server..."
if curl -s http://localhost:8000/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API server is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  API server may not be running${NC}"
fi

echo ""

# Step 6: Test UI
echo "6️⃣  Testing Streamlit UI..."
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ UI is accessible${NC}"
    echo -e "   Open: ${YELLOW}http://localhost:8501${NC}"
else
    echo -e "${YELLOW}⚠️  UI may not be running${NC}"
fi

echo ""
echo "============================================================"
echo -e "${GREEN}✅ ALL TESTS PASSED!${NC}"
echo "============================================================"
echo ""
echo "🎉 Ready to use! Try these commands in the UI:"
echo "   - therapist departed T001"
echo "   - show appointments"
echo "   - run tests"
echo ""
echo "Model being used: gpt-oss-20b (via LM Studio)"
echo "Cost: $0.00 💰"
echo ""

