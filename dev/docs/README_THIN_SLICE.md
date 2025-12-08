# Therapist Replacement System - Thin Slice Demo

## 🎯 Purpose

This is a **mock-first thin slice** implementation that validates the complete architecture for automating therapist replacement when a provider calls in sick.

**Status:** ✅ All mocks working, ready to test

**Next Steps:** Swap mocks to real services one by one (see `MOCKS.md`)

---

## 🚀 Quick Start

### Prerequisites

```bash
# Python 3.9+ required
python3 --version
```

### Run the Demo

```bash
# Navigate to project root
cd /Users/madhan.dhandapani/Documents/schedule

# Run the CLI demo
python3 demo/cli.py
```

### Try the Demo Workflow

```
> therapist departed T001

# Watch the complete workflow execute:
# 1. Trigger - Identifies affected appointments
# 2. Filtering - Eliminates P003 for location
# 3. Scoring - Ranks P001 > P004
# 4. Consent - Patient accepts (mocked)
# 5. Booking - Confirms appointment
# 6. Audit - Generates log

> show audit     # View detailed audit log
> show mocks     # See what's mocked
> help           # Show all commands
> exit           # Exit CLI
```

---

##  📁 Project Structure

```
/Users/madhan.dhandapani/Documents/schedule/
├── MOCKS.md                           # 🔥 Track all mocks & swap instructions
│
├── knowledge/sources/                 # Mock knowledge (txt files)
│   ├── clinic/
│   │   ├── scheduling_policy.txt      # Provider matching rules
│   │   └── scoring_weights.txt        # Scoring factors
│   └── payers/
│       └── medicare_rules.txt         # Medicare POC requirements
│
├── mcp_servers/                       # Mock MCP servers
│   ├── knowledge/server.py            # Knowledge retrieval (MOCKED)
│   └── domain/server.py               # Patient/Provider APIs (MOCKED)
│
├── adapters/llm/
│   └── mock_llm.py                    # Mock LLM (MOCKED - no API calls)
│
├── agents/
│   ├── smart_scheduling_agent.py      # Use Cases 1,2,3,5,6
│   └── patient_engagement_agent.py    # Use Case 4
│
├── orchestrator/
│   └── workflow.py                    # Simple sequential workflow
│
└── demo/
    ├── mock_data.py                   # Test data (Maria, 3 providers)
    └── cli.py                         # Interactive CLI demo
```

---

## 🎭 What's Mocked

| Component | Status | Implementation |
|-----------|--------|---------------|
| **LLM Calls** | 🟡 MOCKED | Returns hardcoded filtering/scoring decisions |
| **LangFuse** | 🟡 MOCKED | Hardcoded prompts (no API) |
| **Knowledge** | 🟡 MOCKED | Reads .txt files with hardcoded responses |
| **Domain APIs** | 🟡 MOCKED | Hardcoded patient/provider data |
| **SMS/Email** | 🟡 MOCKED | Prints to console |
| **Workflow** | 🟢 REAL | Sequential execution (works!) |
| **Event Log** | 🟢 REAL | Python list (works!) |

**See `MOCKS.md` for detailed swap instructions**

---

## 📊 Demo Scenario

### Input
- **Therapist:** Dr. Sarah Johnson (T001) calls in sick
- **Affected:** 1 appointment - Maria Rodriguez (PAT001)
- **Candidates:** 3 providers (P001, P004, P003)

### Expected Output
1. **Filtering:** P003 eliminated (15 miles, exceeds 10 mile limit)
2. **Scoring:** 
   - P001 (Dr. Emily Ross): 75 pts - EXCELLENT
   - P004 (Dr. Michael Lee): 48 pts - ACCEPTABLE
3. **Consent:** Patient accepts via SMS
4. **Booking:** Confirmed with Dr. Emily Ross on Tuesday 11/20 at 10 AM

### Why Dr. Emily Ross Wins
- ✅ Perfect specialty match (Orthopedic)
- ✅ Gender preference match (Female)
- ✅ Perfect day/time match (Tuesday 10 AM)
- ✅ Good availability (60% capacity)
- ❌ No prior relationship (0 continuity points)

---

## 🔧 Testing Individual Components

### Test Mock LLM
```bash
python3 adapters/llm/mock_llm.py
```

### Test Knowledge Server
```bash
python3 mcp_servers/knowledge/server.py
```

### Test Domain Server
```bash
python3 mcp_servers/domain/server.py
```

### Test Smart Scheduling Agent
```bash
python3 agents/smart_scheduling_agent.py
```

### Test Patient Engagement Agent
```bash
python3 agents/patient_engagement_agent.py
```

### Test Workflow Orchestrator
```bash
python3 orchestrator/workflow.py
```

All components have built-in test code when run directly!

---

## 📝 Use Cases Covered

| Use Case | Agent | Status |
|----------|-------|--------|
| UC1: Trigger | Smart Scheduling | ✅ Working |
| UC2: Filtering | Smart Scheduling | ✅ Working |
| UC3: Scoring | Smart Scheduling | ✅ Working |
| UC4: Consent | Patient Engagement | ✅ Working (mocked SMS) |
| UC5: Backfill | Smart Scheduling | 🔴 Simplified (HOD fallback only) |
| UC6: Audit | Smart Scheduling | ✅ Working |

---

## 🔄 Next Steps: Swap Mocks to Real Services

### Day 4: Core Services (HIGH Priority)

**1. Swap Mock LLM → LiteLLM (2 hours)**
```python
# Before:
from adapters.llm.mock_llm import MockLLM
llm = MockLLM()

# After:
from adapters.llm.litellm_adapter import LiteLLMAdapter
llm = LiteLLMAdapter(model="claude-sonnet-4")
```

**2. Swap Mock Prompts → LangFuse (2 hours)**
- Create prompts in LangFuse dashboard
- Update `mock_llm.py` to fetch from LangFuse API

### Week 2: Knowledge Enhancement (MEDIUM Priority)

**3. Convert .txt → .pdf (1 hour)**
- Create/download real PDF documents

**4. Add PDF Parsing (4 hours)**
```bash
pip install pdfplumber pypdf2
```
- Update `mcp_servers/knowledge/server.py`

### Week 3: Data Integration (LOW Priority)

**5. Connect to Real Database/API (8 hours)**
- Option A: Supabase
- Option B: WebPT API

### Week 4: Communication (LOW Priority)

**6. Swap to Twilio + SendGrid (4 hours)**
- Real SMS/Email delivery

---

## 💰 Cost Tracking

| Service | Mock Cost | Real Cost (Monthly) |
|---------|-----------|-------------------|
| LLM (LiteLLM) | $0 | ~$20-50 |
| LangFuse | $0 | $0 (free tier) |
| Vector DB (Optional) | $0 | ~$70 (Pinecone) |
| Database (Optional) | $0 | ~$25 (Supabase) |
| SMS/Email (Optional) | $0 | ~$50 (Twilio+SendGrid) |
| **Total** | **$0** | **~$165-195/month** |

**Recommendation:** Stay with mocks until architecture is validated.

---

## 📚 Documentation

- **`MOCKS.md`** - Complete mock tracking & swap instructions 🔥
- **`docs/USE_CASES.md`** - All 6 use cases detailed
- **`docs/PERSONAS.md`** - User personas & stories
- **`docs/ARCHITECTURE.md`** - System architecture
- **`docs/REQUIREMENTS.md`** - Functional & non-functional requirements
- **`docs/PROCESS.md`** - Complete implementation process

---

## ❓ FAQ

**Q: Why mock-first?**
A: Validates architecture quickly without API costs or integration complexity.

**Q: How long to swap all mocks?**
A: ~2 weeks for full production readiness (see `MOCKS.md`).

**Q: Can I use this with real data?**
A: Yes! Update `demo/mock_data.py` with your patient/provider data.

**Q: Is this production-ready?**
A: Not yet. It's a thin slice for validation. Swap mocks → real services → production.

**Q: What about security/HIPAA?**
A: Mocks don't handle PHI. Add encryption & access controls before production.

---

## 🐛 Troubleshooting

**Problem:** `ModuleNotFoundError`
```bash
# Solution: Ensure you're running from project root
cd /Users/madhan.dhandapani/Documents/schedule
python3 demo/cli.py
```

**Problem:** "No module named 'demo'"
```bash
# Solution: Python path issue. Run from root or add to path
export PYTHONPATH=/Users/madhan.dhandapani/Documents/schedule:$PYTHONPATH
```

**Problem:** Mock responses don't match my data
```bash
# Solution: Mocks are hardcoded for demo. Update:
# - demo/mock_data.py (test data)
# - adapters/llm/mock_llm.py (responses)
```

---

## 🎉 Success Criteria

✅ **Architecture Validated:** All 6 use cases flow end-to-end
✅ **Mocks Working:** Complete workflow with $0 costs
✅ **Documentation Complete:** Clear swap path to real services
✅ **Easy to Demo:** Simple CLI, realistic scenario
✅ **Ready for Next Phase:** Swap to LiteLLM + LangFuse

---

## 📞 Support

Questions? See:
1. **`MOCKS.md`** - Mock swap instructions
2. **`docs/PROCESS.md`** - Complete implementation guide
3. Individual component test output (run `.py` files directly)

---

**Built with:** Mock-first philosophy ✨  
**Time to implement:** 2-3 days  
**Time to production:** +2-3 weeks (swapping mocks)

🚀 **Ready to test the demo!**




