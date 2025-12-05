.PHONY: help dev cli install clean clean-all docker-build docker-up docker-down docker-logs config test test-template

# Default target
.DEFAULT_GOAL := help

# Virtual environment directory
VENV := venv

help: ## Show this help message
	@echo ""
	@echo "╔═══════════════════════════════════════════════════════════════╗"
	@echo "║                                                               ║"
	@echo "║      Healthcare Operations Assistant - Command Reference     ║"
	@echo "║                                                               ║"
	@echo "╚═══════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 QUICK START"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make install"
	@echo "    └─ Install Python dependencies in virtual environment"
	@echo "    └─ Run this FIRST before anything else"
	@echo ""
	@echo "  make dev"
	@echo "    └─ Resets demo data and starts all services (API + UI)"
	@echo "    └─ Auto-detects and kills port conflicts"
	@echo "    └─ Always starts with fresh demo state"
	@echo "    └─ Uses LM Studio (localhost:1234) - no login needed"
	@echo "    └─ API:  http://localhost:8000"
	@echo "    └─ UI:   http://localhost:8501"
	@echo ""
	@echo "  make stop"
	@echo "    └─ Stop all running services cleanly"
	@echo "    └─ Removes PID files and cleans up processes"
	@echo ""
	@echo "📊 MONITORING & DEBUGGING"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make status"
	@echo "    └─ Check if services are running (shows PIDs and URLs)"
	@echo ""
	@echo "  make logs"
	@echo "    └─ View last 20 lines from API and UI logs"
	@echo "    └─ Logs saved in: logs/api.log, logs/ui.log"
	@echo ""
	@echo "  make restart"
	@echo "    └─ Stop and start all services (full restart)"
	@echo "    └─ Also resets demo data to initial state"
	@echo ""
	@echo "🐳 DOCKER COMMANDS"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make docker-build"
	@echo "    └─ Build all Docker images from docker-compose.yml"
	@echo ""
	@echo "  make docker-up"
	@echo "    └─ Start all services in Docker containers"
	@echo "    └─ Includes: UI, API, LiteLLM proxy, PostgreSQL"
	@echo "    └─ LiteLLM UI: http://localhost:4000"
	@echo "    └─ LiteLLM Login: admin / LITELLM_MASTER_KEY (default: sk-1234)"
	@echo ""
	@echo "  make docker-down"
	@echo "    └─ Stop all Docker containers"
	@echo ""
	@echo "  make docker-logs"
	@echo "    └─ Stream logs from all Docker containers (live)"
	@echo ""
	@echo "  make docker-restart"
	@echo "    └─ Restart all Docker containers"
	@echo ""
	@echo "  make docker-clean"
	@echo "    └─ Remove all containers, volumes, and networks"
	@echo "    └─ WARNING: This deletes data!"
	@echo ""
	@echo "⚙️  CONFIGURATION"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make config"
	@echo "    └─ Show current LLM configuration (timeouts, tokens, etc)"
	@echo "    └─ Edit: .env or config/llm_settings.py"
	@echo ""
	@echo "🔧 DEVELOPMENT & TESTING"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  make test"
	@echo "    └─ Run all workflow tests (test_all_stages.py)"
	@echo "    └─ Tests all 7 use case scenarios"
	@echo ""
	@echo "  make reset-demo"
	@echo "    └─ Reset demo data to initial state"
	@echo "    └─ Sets up: Sarah (3 appts), Michael (unavailable)"
	@echo "    └─ Use this to run demo multiple times"
	@echo ""
	@echo "  make cli"
	@echo "    └─ Run the interactive command-line interface"
	@echo "    └─ Alternative to the web UI"
	@echo ""
	@echo "  make clean"
	@echo "    └─ Remove Python cache files (__pycache__, *.pyc)"
	@echo ""
	@echo "  make clean-all"
	@echo "    └─ Remove virtual environment + all generated files"
	@echo "    └─ Use this for a fresh start"
	@echo ""
	@echo "💡 COMMON WORKFLOWS"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  First time setup:"
	@echo "    make install && make dev"
	@echo ""
	@echo "  Daily development:"
	@echo "    make dev          # Start services"
	@echo "    make status       # Check they're running"
	@echo "    make logs         # View logs if issues"
	@echo "    make stop         # Stop when done"
	@echo ""
	@echo "  Troubleshooting:"
	@echo "    make stop && make dev     # Force restart"
	@echo "    tail -f logs/api.log      # Live API logs"
	@echo "    tail -f logs/ui.log       # Live UI logs"
	@echo ""
	@echo "  Docker workflow:"
	@echo "    make docker-build && make docker-up"
	@echo ""
	@echo "📚 DOCUMENTATION"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  README.md                 - Project overview"
	@echo "  QUICKSTART.md             - Quick start guide"
	@echo "  docs/DEMO_STORY.md        - Demo scenarios"
	@echo "  docs/USE_CASES.md         - Detailed use cases"
	@echo ""
	@echo "🌐 URLS (when running)"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Chat UI:      http://localhost:8501/"
	@echo "  API Docs:     http://localhost:8000/docs"
	@echo "  Calendar:     http://localhost:8000/schedule.html"
	@echo "  Emails:       http://localhost:8000/emails.html"
	@echo "  Health:       http://localhost:8000/health"
	@echo ""
	@echo "🤖 LLM SETUP"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "  Local Dev (make dev):"
	@echo "    • Uses LM Studio directly (no login)"
	@echo "    • API: http://localhost:1234/v1"
	@echo "    • Open LM Studio → Load model → Start Local Server"
	@echo ""
	@echo "  Docker (make docker-up):"
	@echo "    • Uses LiteLLM Proxy with Web UI"
	@echo "    • URL: http://localhost:4000"
	@echo "    • Username: admin"
	@echo "    • Password: sk-1234 (or set LITELLM_MASTER_KEY)"
	@echo ""

dev: ## Start API and UI (both services in background)
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@echo "🔄 Resetting demo data to initial state..."
	@./scripts/reset-demo.sh
	@echo ""
	@mkdir -p logs
	@./scripts/start.sh

cli: ## Run the interactive CLI demo
	@echo "Starting interactive CLI..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@bash -c "source $(VENV)/bin/activate && python demo/cli.py"

install: ## Install Python dependencies in virtual environment
	@echo "Setting up virtual environment..."
	@if [ ! -d "$(VENV)" ]; then \
		python3 -m venv $(VENV); \
	fi
	@echo "Installing dependencies..."
	@bash -c "source $(VENV)/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"
	@echo "✅ Installation complete! Run 'make dev' to start."

stop: ## Stop all services (API + UI)
	@./scripts/stop.sh

status: ## Check status of all services
	@./scripts/status.sh

logs: ## View logs from all services
	@echo "📋 Recent logs (Ctrl+C to exit):"
	@echo ""
	@echo "════════ API Server ════════"
	@tail -20 logs/api.log 2>/dev/null || echo "No API logs yet"
	@echo ""
	@echo "════════ Streamlit UI ════════"
	@tail -20 logs/ui.log 2>/dev/null || echo "No UI logs yet"

restart: stop dev ## Restart all services

reset-demo: ## Reset all data to initial state for testing
	@./scripts/reset-demo.sh

clean: ## Remove Python cache files
	@echo "Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cache cleaned"

clean-all: clean ## Remove virtual environment and all generated files
	@echo "Removing virtual environment..."
	@rm -rf $(VENV)
	@echo "✅ Complete cleanup done"

# Docker commands
docker-build: ## Build Docker images
	@echo "Building Docker images..."
	@docker-compose build

docker-up: ## Start all services in Docker (detached mode)
	@echo "Starting Docker services..."
	@docker-compose up -d
	@echo ""
	@echo "✅ Services started!"
	@echo "  - UI:       http://localhost:8501"
	@echo "  - API:      http://localhost:8000"
	@echo "  - LiteLLM:  http://localhost:4000"
	@echo ""
	@echo "View logs: make docker-logs"
	@echo "Stop:      make docker-down"

docker-down: ## Stop all Docker services
	@echo "Stopping Docker services..."
	@docker-compose down
	@echo "✅ Services stopped"

docker-logs: ## View logs from all Docker services
	@docker-compose logs -f

docker-restart: ## Restart all Docker services
	@echo "Restarting Docker services..."
	@docker-compose restart
	@echo "✅ Services restarted"

docker-clean: ## Remove all containers, volumes, and images
	@echo "Cleaning Docker resources..."
	@docker-compose down -v
	@echo "✅ Docker cleaned"

test: ## Run all tests
	@echo "Running tests..."
	@if [ ! -d "$(VENV)" ]; then \
		echo "Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@bash -c "source $(VENV)/bin/activate && python test_all_stages.py"

test-template: ## Test template-driven orchestrator with LM Studio
	@echo "🧪 Testing template-driven orchestrator with LM Studio..."
	@echo ""
	@echo "Prerequisites:"
	@echo "  1. LM Studio running at localhost:1234"
	@echo "  2. Model loaded (e.g., openai/gpt-oss-20b)"
	@echo ""
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@bash -c "source $(VENV)/bin/activate && python test_template_lmstudio.py"

config: ## Show current LLM configuration settings
	@echo "⚙️  Current LLM Configuration:"
	@echo ""
	@if [ ! -d "$(VENV)" ]; then \
		echo "❌ Virtual environment not found. Run 'make install' first."; \
		exit 1; \
	fi
	@bash -c "source $(VENV)/bin/activate && python -c 'from config.llm_settings import LLMSettings; LLMSettings.print_settings()'"
