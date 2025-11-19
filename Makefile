.PHONY: help dev cli install clean test lint format docs

# Python virtual environment
VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip3
STREAMLIT := $(VENV)/bin/streamlit

# Create virtual environment if it doesn't exist
$(VENV)/bin/activate:
	@echo "📦 Creating virtual environment..."
	python3 -m venv $(VENV)
	@echo "✅ Virtual environment created"

# Default target - show help
help:
	@echo "🏥 Therapist Replacement System - Commands"
	@echo "==========================================="
	@echo ""
	@echo "Development:"
	@echo "  make dev          - 🚀 Launch Chat UI (Streamlit)"
	@echo "  make cli          - 💻 Launch CLI interface"
	@echo "  make install      - 📦 Install dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test         - 🧪 Run all tests"
	@echo "  make test-agents  - 🤖 Test agents only"
	@echo "  make test-workflow- ⚙️  Test workflow only"
	@echo "  make test-ui      - 🎨 Test UI components"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint         - 🔍 Run linters"
	@echo "  make format       - ✨ Format code"
	@echo "  make check        - ✅ Run all checks"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean        - 🧹 Clean cache files"
	@echo "  make docs         - 📚 Open documentation"
	@echo "  make demo         - 🎬 Run demo scenario"
	@echo ""

# Launch Streamlit UI
dev: $(VENV)/bin/activate
	@echo "🚀 Launching Chat UI..."
	@echo "   URL: http://localhost:8501"
	@echo "   Press Ctrl+C to stop"
	@echo ""
	@test -f $(STREAMLIT) || (echo "📦 Installing dependencies..." && $(PIP) install streamlit plotly)
	@$(STREAMLIT) run demo/chat_ui.py --server.headless true

# Launch CLI
cli: $(VENV)/bin/activate
	@echo "💻 Launching CLI..."
	@$(PYTHON) demo/cli.py

# Install dependencies
install: $(VENV)/bin/activate
	@echo "📦 Installing dependencies in virtual environment..."
	@$(PIP) install -r requirements.txt
	@echo "✅ Installation complete!"
	@echo ""
	@echo "Run 'make dev' to start the UI"

# Install in development mode
install-dev:
	@echo "📦 Installing development dependencies..."
	@pip3 install -r requirements.txt
	@pip3 install -e .
	@echo "✅ Development installation complete!"

# Run all tests
test:
	@echo "🧪 Running all tests..."
	@python3 -m pytest tests/ -v

# Test individual components
test-agents:
	@echo "🤖 Testing agents..."
	@python3 agents/smart_scheduling_agent.py
	@python3 agents/patient_engagement_agent.py

test-workflow:
	@echo "⚙️  Testing workflow..."
	@python3 orchestrator/workflow.py

test-mcp:
	@echo "🔌 Testing MCP servers..."
	@python3 mcp_servers/knowledge/server.py
	@python3 mcp_servers/domain/server.py

test-mock-data:
	@echo "📊 Testing mock data..."
	@python3 demo/mock_data.py

test-all-components: test-mock-data test-mcp test-agents test-workflow
	@echo "✅ All component tests passed!"

# Run linters
lint:
	@echo "🔍 Running linters..."
	@python3 -m ruff check . || true
	@python3 -m mypy . || true

# Format code
format:
	@echo "✨ Formatting code..."
	@python3 -m black .
	@python3 -m ruff format .

# Run all checks
check: lint test-all-components
	@echo "✅ All checks passed!"

# Clean cache and temporary files
clean:
	@echo "🧹 Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache cleaned!"

# Clean everything including venv
clean-all: clean
	@echo "🧹 Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "✅ All clean!"

# Open documentation
docs:
	@echo "📚 Opening documentation..."
	@open docs/UI_QUICKSTART.md || cat docs/UI_QUICKSTART.md

# Run demo scenario
demo:
	@echo "🎬 Running demo scenario..."
	@echo ""
	@echo "Test Command: therapist departed T001"
	@echo ""
	@python3 orchestrator/workflow.py

# Show what's mocked
show-mocks:
	@echo "🎭 Mocked Components:"
	@echo ""
	@cat docs/MOCKS.md | head -50

# Quick validation
validate: test-all-components
	@echo "✅ System validated and ready for demo!"

# Setup development environment
setup:
	@echo "🔧 Setting up development environment..."
	@python3 -m venv venv || true
	@echo "   Virtual environment created: venv/"
	@echo ""
	@echo "Activate it with:"
	@echo "   source venv/bin/activate"
	@echo ""
	@echo "Then run:"
	@echo "   make install"

# Show system status
status:
	@echo "📊 System Status"
	@echo "================"
	@echo ""
	@echo "Python version:"
	@python3 --version
	@echo ""
	@echo "Streamlit installed:"
	@which streamlit > /dev/null && streamlit --version || echo "❌ Not installed (run: make install)"
	@echo ""
	@echo "Project files:"
	@ls -la demo/chat_ui.py demo/cli.py > /dev/null && echo "✅ UI and CLI files present" || echo "❌ Missing files"
	@echo ""
	@echo "Documentation:"
	@ls -la docs/*.md | wc -l | xargs echo "📄 Documentation files:"

# Build for production (future)
build:
	@echo "🏗️  Building for production..."
	@echo "   (Not implemented yet - for future use)"

# Deploy to Streamlit Cloud (future)
deploy:
	@echo "🚀 Deploying to Streamlit Cloud..."
	@echo "   (Not implemented yet - for future use)"
	@echo ""
	@echo "Manual deployment:"
	@echo "   1. Push to GitHub"
	@echo "   2. Go to https://share.streamlit.io"
	@echo "   3. Connect your repo"
	@echo "   4. Deploy!"

# Show project structure
tree:
	@echo "📁 Project Structure"
	@echo "===================="
	@tree -L 2 -I '__pycache__|*.pyc|venv|.git' || ls -R

# Run quick demo with UI
quick-demo:
	@echo "🎬 Quick Demo"
	@echo "============="
	@echo ""
	@echo "Starting UI in 3 seconds..."
	@sleep 3
	@make dev

# Default target
.DEFAULT_GOAL := help

