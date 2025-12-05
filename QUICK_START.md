# 🚀 Quick Start Guide

## One Command to Start Everything

```bash
make dev
```

That's it! 🎉

## What You'll See

```
🤖 LLM Configuration:
   Provider: LM Studio (Local)
   Model: openai/gpt-oss-20b
   API: http://localhost:1234/v1

✅ API server started (PID: xxxxx)
✅ Streamlit UI started (PID: xxxxx)

════════════════════════════════════════════════════════
✅ All services running!
════════════════════════════════════════════════════════

📱 Application URLs:
   • Chat UI:    http://localhost:8501/
   • API Docs:   http://localhost:8000/docs
   • Calendar:   http://localhost:8000/schedule.html
   • Emails:     http://localhost:8000/emails.html

🤖 LLM Provider (Local Development):
   • Provider:   LM Studio
   • API:        http://localhost:1234/v1
   • Model:      openai/gpt-oss-20b
   • Status:     Connecting directly to LM Studio

💡 LM Studio Setup:
   1. Open LM Studio app
   2. Load model: openai/gpt-oss-20b
   3. Start 'Local Server' (port 1234)
   4. No login required - direct API access

🐳 Docker Setup (Optional):
   To use LiteLLM proxy with Web UI instead:
   • Run: make docker-up
   • LiteLLM UI:  http://localhost:4000
   • Username:    admin
   • Password:    Set via LITELLM_MASTER_KEY (default: sk-1234)
```

## Two Modes of Operation

### Mode 1: Local Development (Default - `make dev`)
- ✅ **Direct connection to LM Studio**
- ✅ No proxy, no login
- ✅ Fast and simple
- ✅ Perfect for development

**LLM Access:**
- API: `http://localhost:1234/v1`
- No UI - direct API access
- No login required

### Mode 2: Docker with LiteLLM Proxy (`make docker-up`)
- ✅ **Full production-like setup**
- ✅ LiteLLM proxy with Web UI
- ✅ Multi-model support
- ✅ Cost tracking & monitoring

**LiteLLM Proxy Access:**
- URL: `http://localhost:4000`
- Username: `admin`
- Password: `sk-1234` (default, set via `LITELLM_MASTER_KEY`)

## Quick Commands

| Command | Description |
|---------|-------------|
| `make dev` | Start everything (local mode) |
| `make stop` | Stop all services |
| `make logs` | View logs |
| `make help` | Show all commands |
| `make docker-up` | Start with Docker + LiteLLM proxy |
| `make docker-down` | Stop Docker services |

## Prerequisites

### For Local Development (`make dev`)
1. **LM Studio** must be running
   - Download: https://lmstudio.ai/
   - Load model: `openai/gpt-oss-20b`
   - Start Local Server (port 1234)

2. **Python 3.9+** installed

3. **Virtual environment** set up
   ```bash
   make install
   ```

### For Docker Mode (`make docker-up`)
1. **Docker** installed and running
2. **Docker Compose** installed

## Testing the Setup

### 1. Check Services are Running
```bash
make status
```

### 2. Test the Workflow
1. Open Calendar: http://localhost:8000/schedule.html
2. Click "🚫 Mark Unavailable" on Dr. Sarah Johnson
3. Watch the AI workflow:
   - ✅ Intelligent provider matching
   - ✅ Personalized email generation
   - ✅ Automatic reassignment

### 3. Check Results
- View emails: http://localhost:8000/emails.html
- Check logs: `make logs`

## Troubleshooting

### "Connection error" when marking unavailable
**Problem:** LM Studio is not running or not accessible

**Solution:**
1. Open LM Studio
2. Load model: `openai/gpt-oss-20b`
3. Click "Start Server" (port 1234)
4. Restart services: `make stop && make dev`

### Ports already in use
**No problem!** `make dev` automatically kills processes on ports 8000 & 8501.

### Want to use cloud APIs instead?
Edit `scripts/start.sh` and change:
```bash
export LITELLM_BASE_URL="https://api.anthropic.com"
export LITELLM_API_KEY="your-api-key"
export LITELLM_DEFAULT_MODEL="claude-sonnet-4"
```

## What `make dev` Does Automatically

1. ✅ Kills existing processes (ports 8000, 8501)
2. ✅ Resets demo data to initial state
3. ✅ Exports LM Studio configuration
4. ✅ Starts API server with LLM enabled
5. ✅ Starts UI server
6. ✅ Shows all URLs and credentials

**No manual configuration needed!**

## Help

```bash
make help
```

Shows complete list of commands and URLs.

---

**Remember:** Just run `make dev` and you're good to go! 🚀

