# 🏥 Therapist Replacement System

**Automated provider matching powered by AI agents**

When a therapist calls in sick, this system automatically finds the best replacement and reschedules appointments using intelligent matching algorithms.

---

## 🚀 Quick Start

### Option 1: Docker (Recommended - Includes LiteLLM)

```bash
# Start all services (API + UI + LiteLLM)
make docker-up

# Access UI at http://localhost:8501
# Access LiteLLM at http://localhost:4000
```

### Option 2: Local Development

```bash
# Start API and UI locally
make dev

# Opens at http://localhost:8501
```

### Option 3: CLI

```bash
make cli
```

Traditional command-line interface for automation/scripts.

---

## 📦 Installation

```bash
# Install dependencies
make install

# Or manually
pip3 install -r requirements.txt
```

---

## 🎯 Demo It!

**In the UI:**
1. Run: `make dev`
2. Type: `therapist departed T001`
3. Watch the workflow execute!

**In the CLI:**
1. Run: `make cli`
2. Type: `therapist departed T001`
3. See the results!

---

## 📋 Available Commands

```bash
make help          # Show all commands

# Docker (Recommended)
make docker-up       # 🐳 Start all services (API + UI + LiteLLM)
make docker-down     # 🛑 Stop all services
make docker-logs     # 📋 View logs
make docker-restart  # 🔄 Restart services
make docker-clean    # 🧹 Clean Docker resources

# Local Development
make dev           # 🚀 Launch Chat UI + API locally
make cli           # 💻 Launch CLI
make install       # 📦 Install dependencies

# Testing
make test          # 🧪 Run all tests

# Utilities
make clean         # 🧹 Clean cache
make clean-all     # 🗑️ Remove venv + cache
```

---

## 🎬 What This Demo Does

### Scenario
Dr. Sarah Johnson (T001) calls in sick. The system automatically:

1. **🚨 Trigger** - Identifies affected appointments (Maria Rodriguez)
2. **🔍 Filtering** - Eliminates unqualified providers (P003: too far)
3. **⭐ Scoring** - Ranks providers using 5 factors (150 points max)
   - Dr. Emily Ross: **75 points** (EXCELLENT)
   - Dr. Michael Lee: **48 points** (ACCEPTABLE)
4. **💬 Consent** - Gets patient approval via SMS
5. **📅 Booking** - Confirms with Dr. Ross on Tuesday 11/20 at 10 AM
6. **📊 Audit** - Generates complete log

### Winner
**Dr. Emily Ross** wins because:
- ✅ Perfect orthopedic specialty match (35/35 pts)
- ✅ Female provider matching preference (30/30 pts)
- ✅ Tuesday 10 AM exact time match (20/20 pts)
- ✅ Good availability at 60% capacity (10/25 pts)

---

## 🎭 Three Modes Available

### Option 1: Mock Mode (Default) - **$0/month**
- 🟡 Hardcoded LLM responses
- ✅ Perfect for initial demos
- ✅ No setup needed
```bash
make docker-up
```

### Option 2: Local Model (LM Studio) - **$0/month** ⭐ NEW
- ✅ **FREE** - No API costs!
- ✅ Private - data stays on your machine
- ✅ Fast (with GPU)
- 📚 Best for development & testing

```bash
# 1. Download LM Studio: https://lmstudio.ai
# 2. Start server (port 1234)
# 3. Configure
bash scripts/setup-env.sh
nano .env
# Set: USE_MOCK_LLM=false
# Set: USE_LOCAL_MODEL=true

# 4. Start
make docker-up
```

**See:** `docs/LM_STUDIO_SETUP.md` for complete guide

### Option 3: Cloud API (Anthropic/OpenAI) - **$50-150/month**
- ✅ Best quality
- ✅ No hardware needed
- ✅ Very fast
- ⚠️ Costs money (budget-protected at $5/day)

```bash
# 1. Get API key: https://console.anthropic.com
# 2. Configure
bash scripts/setup-env.sh
nano .env
# Set: ANTHROPIC_API_KEY=sk-ant-api03-...
# Set: USE_MOCK_LLM=false
# Set: USE_LOCAL_MODEL=false

# 3. Start
make docker-up
```

**LiteLLM Features:**
- ✅ Unified API for all providers
- ✅ Auto fallbacks (local → Claude → GPT-4)
- ✅ Cost tracking ($5/day limit)
- ✅ Request caching
- ✅ Rate limiting

**Recommended Strategy:**
- **Dev/Testing**: Local models (FREE)
- **Staging**: Claude Haiku ($10-20/month)
- **Production**: Claude Sonnet ($50-150/month)

---

## 📁 Project Structure

```
.
├── demo/
│   ├── chat_ui.py          # Streamlit web UI ⭐ NEW
│   ├── cli.py              # CLI interface
│   └── mock_data.py        # Test data
├── agents/
│   ├── smart_scheduling_agent.py
│   └── patient_engagement_agent.py
├── mcp_servers/
│   ├── knowledge/          # Rules & policies
│   └── domain/             # Patient/provider APIs
├── adapters/
│   └── llm/
│       ├── mock_llm.py     # Mocked LLM
│       └── litellm_adapter.py  # Real LLM (future)
├── orchestrator/
│   └── workflow.py         # 6-stage workflow
├── docs/                   # 📚 Complete documentation
│   ├── UI_QUICKSTART.md
│   ├── MOCKS.md
│   ├── ARCHITECTURE.md
│   └── ...
├── Makefile               # 🔧 Easy commands
└── requirements.txt       # Python dependencies
```

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| **`docs/LM_STUDIO_SETUP.md`** | Use FREE local models (LM Studio) ⭐ NEW |
| **`docker/README.md`** | Docker deployment guide |
| **`DOCKER_SETUP.md`** | Quick Docker + LiteLLM setup |
| **`config/cost_limits.yaml`** | Detailed cost breakdown |
| **`docs/UI_QUICKSTART.md`** | How to use the web UI |
| **`docs/MOCKS.md`** | What's mocked & how to swap |
| **`DEMO_GUIDE.md`** | Patient email simulation guide |
| **`DEMO_STORY.md`** | Simple demo narrative |
| **`docs/LANGGRAPH_EXPLAINED.md`** | LangGraph workflow explanation |
| **`docs/USE_CASES_SIMPLIFIED.md`** | 6 use cases (current demo) ⭐ |
| **`docs/USE_CASES.md`** | 6 use cases (full vision) |

---

## 🔄 Next Steps

### Immediate (5 minutes)
```bash
# Option A: Docker (includes LiteLLM)
make docker-up

# Option B: Local development
make install && make dev
```

### Week 1 (Swap to Real LLM) - **~2 hours**
```bash
# 1. Get Anthropic API key
# Sign up at https://console.anthropic.com

# 2. Configure .env
cp .env.example .env
# Add: ANTHROPIC_API_KEY=sk-ant-api03-...

# 3. Start with real LLM
USE_MOCK_LLM=false make docker-up

# 4. Test
# Type: "therapist departed T001"
# Watch real Claude AI make decisions!
```

**Benefits:**
- ✅ Real AI decision making
- ✅ Adapts to complex scenarios
- ✅ No hardcoded logic
- ✅ Better than rule-based systems

### Week 2-4 (Production Ready) - **~3 weeks**
- [ ] Add PDF parsing for compliance documents
- [ ] Connect to WebPT API / database
- [ ] Add real SMS/email (Twilio/SendGrid)
- [ ] Add authentication (OAuth)
- [ ] Deploy to cloud (AWS/Azure/GCP)
- [ ] Add monitoring (Prometheus/Grafana)

See `docker/README.md` for deployment guide.

---

## 🎨 UI vs CLI

### Web UI (Streamlit) - **Recommended for Demos**
- ✅ Modern ChatGPT-like interface
- ✅ Visual workflow stages with tabs
- ✅ Interactive tables for scores
- ✅ Export to JSON
- ✅ Sidebar with quick commands
- ✅ Perfect for stakeholder demos

### CLI - **Good for Automation**
- ✅ Terminal-based
- ✅ Scriptable
- ✅ Good for CI/CD
- ✅ Lower resource usage

**Both interfaces use the same backend!**

---

## 🧪 Testing

```bash
# Test all components
make test-all-components

# Test individual pieces
make test-agents      # Smart Scheduling & Patient Engagement agents
make test-workflow    # Workflow orchestrator
make test-mcp         # MCP servers

# Validate everything
make validate
```

All tests should pass! ✅

---

## 💰 Cost Comparison

| Mode | Setup | Per Workflow | Monthly (100 workflows/day) |
|------|-------|--------------|----------------------------|
| **Mock** | None | $0 | $0 |
| **Local Model** ⭐ | LM Studio | $0 | **$0** |
| **Cloud API** | API key | $0.035 | $50-150 (budget-protected) |

### Local Model (LM Studio) - FREE!
- ✅ **$0/month** - No API costs
- ✅ Unlimited workflows
- ✅ 100% private
- ⚠️ Requires good computer (8GB+ RAM, GPU recommended)

### Cloud API (Budget-Protected)
- **Hard cap**: $5/day (enforced by LiteLLM)
- **Max monthly**: $150 (30 days × $5)
- **Typical**: $50-75/month (50-100 workflows/day)
- **Alert**: $4/day (80% threshold)

**Daily Usage:**
- 10 workflows = $0.35/day = ~$10/month
- 50 workflows = $1.75/day = ~$50/month  
- 100 workflows = $3.50/day = ~$100/month
- 140+ workflows = Budget limit hit

**Full Stack (Production):**
- LLM: $0 (local) or $50-150 (cloud)
- Database: ~$25 (Supabase)
- SMS/Email: ~$50 (Twilio/SendGrid)
- **Total**: $75-225/month

See `config/cost_limits.yaml` for detailed breakdown.

---

## 🐛 Troubleshooting

### Issue: `make dev` fails

```bash
# Solution: Install Streamlit
make install

# Or manually
pip3 install streamlit plotly
```

### Issue: Python version

```bash
# Requires Python 3.9+
python3 --version

# Check system status
make status
```

### Issue: Port already in use

```bash
# Use different port
streamlit run demo/chat_ui.py --server.port 8502
```

---

## 🤝 Contributing

This is a demo/prototype system. Future enhancements:
- [ ] Add more test scenarios
- [ ] Add real PDF parsing
- [ ] Connect to real database
- [ ] Add authentication
- [ ] Deploy to cloud

---

## 📞 Support

**Questions?**
1. Read `docs/UI_QUICKSTART.md` for UI help
2. Read `docs/MOCKS.md` for mock swapping
3. Run `make help` for all commands

---

## ⚡ TL;DR

### Quick Start (Docker)
```bash
# Start everything (API + UI + LiteLLM)
make docker-up

# Open browser
open http://localhost:8501

# Type command
therapist departed T001

# 🎉 Watch it work!
```

### Quick Start (Local)
```bash
# Install
make install

# Run UI + API
make dev

# Try it
therapist departed T001
```

---

**Built with:** LangGraph + Streamlit + LiteLLM + MCP  
**Architecture:** Modular, vendor-agnostic, production-ready  
**Timeline:** 5 min (demo) → 2 hours (real LLM) → 3 weeks (production)  
**Cost:** $0 (mocks) → $50-75/month (LLM) → $125-150/month (full stack)  
**Budget:** **$5/day hard limit** (protected by LiteLLM)

🚀 **Ready to demo!** 🐳 **Docker-ready!** 💰 **Budget-protected!**

