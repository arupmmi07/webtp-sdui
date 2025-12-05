#!/bin/bash
# Setup script for creating .env file

set -e

echo "=================================================="
echo "  Healthcare Operations Assistant - Setup"
echo "=================================================="
echo ""

ENV_FILE=".env"

if [ -f "$ENV_FILE" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Overwrite? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

echo "Creating .env file..."

cat > "$ENV_FILE" << 'EOF'
# LiteLLM Configuration
LITELLM_MASTER_KEY=sk-1234

# LLM Mode Selection
USE_MOCK_LLM=false  # Set to 'true' to use hardcoded mock responses (for demos)
USE_LOCAL_MODEL=true  # Set to 'true' to use LM Studio (FREE)

# Model Configuration
LITELLM_DEFAULT_MODEL=gpt-oss-20b  # Options: gpt-oss-20b, local-llama, local-mistral, claude-sonnet-4

# LLM Provider API Keys (only needed if USE_LOCAL_MODEL=false)
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENAI_API_KEY=your-openai-key-here
AZURE_API_KEY=your-azure-key-here

# LangFuse (Observability)
LANGFUSE_PUBLIC_KEY=your-langfuse-public-key
LANGFUSE_SECRET_KEY=your-langfuse-secret-key
LANGFUSE_HOST=https://cloud.langfuse.com

# Database (for LiteLLM)
DATABASE_URL=postgresql://postgres:postgres@litellm-db:5432/litellm
EOF

echo "✅ .env file created!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Next Steps:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Test with Mock LLM (No setup needed)"
echo "    make docker-up"
echo ""
echo "2️⃣  Use Local Model - FREE (via LM Studio)"
echo "    - Download LM Studio: https://lmstudio.ai"
echo "    - Start LM Studio server (port 1234)"
echo "    - Edit .env: nano .env"
echo "    - Set: USE_MOCK_LLM=false"
echo "    - Set: USE_LOCAL_MODEL=true"
echo "    - Run: make docker-restart"
echo "    - See: docs/LM_STUDIO_SETUP.md"
echo ""
echo "3️⃣  Use Cloud API (Requires API key - costs money)"
echo "    - Get key: https://console.anthropic.com"
echo "    - Edit .env: nano .env"
echo "    - Set: ANTHROPIC_API_KEY=sk-ant-api03-..."
echo "    - Set: USE_MOCK_LLM=false"
echo "    - Set: USE_LOCAL_MODEL=false"
echo "    - Run: make docker-restart"
echo ""
echo "4️⃣  Open UI"
echo "    http://localhost:8501"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

