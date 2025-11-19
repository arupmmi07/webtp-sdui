# 🏥 Therapist Replacement System

**Automated provider matching powered by AI agents**

When a therapist calls in sick, this system automatically finds the best replacement and reschedules appointments using intelligent matching algorithms.

---

## 🚀 Quick Start

### Option 1: Launch UI (Recommended)

```bash
make dev
```

This opens a **ChatGPT-like web interface** at http://localhost:8501

### Option 2: Launch CLI

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

# Development
make dev           # 🚀 Launch Chat UI
make cli           # 💻 Launch CLI
make install       # 📦 Install dependencies

# Testing
make test          # 🧪 Run all tests
make test-agents   # 🤖 Test agents
make validate      # ✅ Validate system

# Utilities
make clean         # 🧹 Clean cache
make docs          # 📚 Open docs
make status        # 📊 System status
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

## 🎭 Mock Mode

Currently running in **mock mode**:
- 🟡 No real LLM API calls (hardcoded responses)
- 🟡 No real SMS/email (prints to console)
- 🟡 Using test data (Maria + 3 providers)
- 🟢 Real workflow orchestration
- 🟢 Real event logging

**Cost:** $0 (fully mocked)

See `docs/MOCKS.md` for how to swap to real services.

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
| **`docs/UI_QUICKSTART.md`** | How to use the web UI |
| **`docs/MOCKS.md`** | What's mocked & how to swap |
| **`docs/QUICKSTART_DEMO.md`** | 30-second quick start |
| **`docs/ARCHITECTURE.md`** | System architecture |
| **`docs/USE_CASES.md`** | All 6 use cases |
| **`docs/CHAT_UI_COMPARISON.md`** | Why we chose Streamlit |

---

## 🔄 Next Steps

### Immediate
1. ✅ Run the demo: `make dev`
2. ✅ Test the workflow: `therapist departed T001`
3. ✅ Show to stakeholders

### Week 1 (Swap to Real LLM)
1. Get API keys (Anthropic, LangFuse)
2. Run: `pip install litellm langfuse`
3. Change 1 line in agent code
4. Test with real AI decisions
5. **Effort:** ~4 hours

### Week 2-4 (Production Ready)
- Add PDF parsing for knowledge
- Connect to database/WebPT API
- Add real SMS/email via Twilio/SendGrid
- Deploy to cloud
- **Effort:** ~3 weeks

See `docs/MOCKS.md` for detailed swap instructions.

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

## 💰 Cost Tracking

| Component | Mock Cost | Real Cost (Monthly) |
|-----------|-----------|-------------------|
| LLM (LiteLLM) | $0 | ~$20-50 |
| LangFuse | $0 | $0 (free tier) |
| Streamlit | $0 | $0 (open source) |
| Database (optional) | $0 | ~$25 (Supabase) |
| SMS/Email (optional) | $0 | ~$50 (Twilio+SendGrid) |
| **Total** | **$0** | **~$95-125/month** |

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

```bash
# Install
make install

# Run UI
make dev

# Try command
therapist departed T001

# 🎉 Watch it work!
```

---

**Built with:** Mock-first methodology + Streamlit UI  
**Status:** Demo-ready, production-ready architecture  
**Timeline:** 2-3 days to build, 2-3 weeks to production  
**Cost:** $0 (mocks) → $95-125/month (production)

🚀 **Ready to demo!**

