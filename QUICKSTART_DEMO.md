# 🚀 Quick Start - Demo the Thin Slice NOW

## ✅ What's Been Built

A complete **mock-first thin slice** that processes 1 appointment through the entire therapist replacement workflow:

1. ✅ **Trigger** - Identifies affected appointments
2. ✅ **Filtering** - Eliminates unqualified providers (2 filters)
3. ✅ **Scoring** - Ranks providers (2 scoring factors)
4. ✅ **Consent** - Gets patient approval (mocked)
5. ✅ **Booking** - Confirms appointment
6. ✅ **Audit** - Generates complete log

**Status:** READY TO TEST 🎉

---

## 🏃 Run the Demo (30 seconds)

```bash
# Step 1: Navigate to project
cd /Users/madhan.dhandapani/Documents/schedule

# Step 2: Run the CLI
python3 demo/cli.py

# Step 3: Try it!
> therapist departed T001

# Watch the magic happen! 🪄
```

---

## 🎬 What You'll See

```
[STAGE 1] Trigger: Identifying affected appointments...
  → Found 1 affected appointment: Maria Rodriguez

[STAGE 2] Filtering: Applying hard filters...
  ✓ Skills: 3/3 passed
  ✗ Location: 2/3 passed (P003 eliminated: 15 miles away)
  → Qualified: [P001: Dr. Emily Ross, P004: Dr. Michael Lee]

[STAGE 3] Scoring: Ranking qualified providers...
  #1: Dr. Emily Ross - 75 pts (EXCELLENT)
  #2: Dr. Michael Lee - 48 pts (ACCEPTABLE)

[STAGE 4] Consent: Requesting patient approval...
  [SMS MOCK] Offer sent to Maria Rodriguez
  Patient response: YES (after 45 minutes)

[STAGE 5] Booking: Confirming appointment...
  ✓ Appointment confirmed with Dr. Emily Ross
  
[STAGE 6] Audit: Generating audit log...
  ✓ Audit log created

✅ WORKFLOW COMPLETE - All stages successful!

FINAL BOOKING:
  Patient: PAT001 (Maria Rodriguez)
  Provider: P001 (Dr. Emily Ross)
  Date/Time: 2024-11-20 at 10:00 AM
  Confirmation #: CONF-2024-001
```

---

## 🎯 Demo Scenario Details

### The Setup
- **Departed Therapist:** Dr. Sarah Johnson (T001) - sick leave for 2 weeks
- **Affected Patient:** Maria Rodriguez, 55, post-surgical knee rehab
- **Available Providers:** 3 candidates (P001, P004, P003)

### Why Dr. Emily Ross (P001) Wins

| Factor | P001: Dr. Emily Ross | P004: Dr. Michael Lee | P003: Dr. Sarah Park |
|--------|---------------------|---------------------|---------------------|
| **Skills** | ✅ Orthopedic specialist | ✅ General PT (orthopedic trained) | ✅ Orthopedic specialist |
| **Location** | ✅ 2 miles | ✅ 2 miles | ❌ 15 miles (ELIMINATED) |
| **Gender** | ✅ Female (matches pref) | ❌ Male | N/A |
| **Continuity** | ❌ Never seen Maria | ✅ Treated Maria 2 years ago | N/A |
| **Day/Time** | ✅ Tuesday 10 AM (perfect!) | ❌ Thursday 3 PM | N/A |
| **Capacity** | ✅ 60% (good balance) | ❌ 88% (nearly full) | N/A |
| **TOTAL SCORE** | **75/150 - EXCELLENT** | **48/150 - ACCEPTABLE** | **ELIMINATED** |

**Winner:** Dr. Emily Ross - Perfect specialty, gender, and time match!

---

## 🔍 What's Mocked (Important!)

| Component | What You See | Reality |
|-----------|-------------|---------|
| **LLM Calls** | Hardcoded filtering/scoring | Would call Claude via LiteLLM |
| **Knowledge** | Reads .txt files | Would parse .pdf files |
| **Patient Data** | Hardcoded (Maria) | Would query database/WebPT API |
| **SMS** | Prints to console | Would send via Twilio |
| **Patient Response** | Always says "YES" | Would wait for real SMS reply |

**See `MOCKS.md` for complete list and how to swap to real services**

---

## 📋 CLI Commands

```
therapist departed <ID>   - Start replacement workflow
                           Example: therapist departed T001

show audit               - View detailed audit log of last workflow
show mocks               - List all mocked components
help                     - Show all commands
exit                     - Exit CLI
```

---

## 🧪 Test Individual Components

Want to test components separately?

```bash
# Test Mock LLM
python3 adapters/llm/mock_llm.py

# Test Knowledge Server
python3 mcp_servers/knowledge/server.py

# Test Domain Server  
python3 mcp_servers/domain/server.py

# Test Smart Scheduling Agent
python3 agents/smart_scheduling_agent.py

# Test Patient Engagement Agent
python3 agents/patient_engagement_agent.py

# Test Full Workflow
python3 orchestrator/workflow.py
```

Each component has built-in test code!

---

## 📁 Key Files Created

### Core Implementation
- `adapters/llm/mock_llm.py` - Mock LLM with hardcoded decisions
- `mcp_servers/knowledge/server.py` - Mock knowledge retrieval
- `mcp_servers/domain/server.py` - Mock patient/provider APIs
- `agents/smart_scheduling_agent.py` - Filtering & scoring logic
- `agents/patient_engagement_agent.py` - Patient communication
- `orchestrator/workflow.py` - Workflow orchestration
- `demo/cli.py` - Interactive demo

### Test Data & Knowledge
- `demo/mock_data.py` - Maria + 3 providers
- `knowledge/sources/clinic/scheduling_policy.txt` - Matching rules
- `knowledge/sources/clinic/scoring_weights.txt` - Scoring factors
- `knowledge/sources/payers/medicare_rules.txt` - Medicare POC rules

### Documentation
- `MOCKS.md` - 🔥 Complete mock tracking & swap guide
- `README_THIN_SLICE.md` - Full system documentation
- `QUICKSTART_DEMO.md` - This file!

---

## 🔄 Next Steps

### Immediate (You can do now)
1. ✅ Run the demo: `python3 demo/cli.py`
2. ✅ Test with command: `therapist departed T001`
3. ✅ View audit: `show audit`
4. ✅ Check mocks: `show mocks`

### Day 4 (Swap to Real LLM)
1. Get API keys (Anthropic, LangFuse)
2. Install: `pip install litellm langfuse`
3. Update 1 line: `MockLLM()` → `LiteLLMAdapter()`
4. See real LLM decisions!

### Week 2-4 (Production Ready)
- Add real PDF parsing
- Connect to database/WebPT
- Add real SMS/Email
- Deploy to cloud

**See `MOCKS.md` for detailed swap instructions**

---

## 💡 Pro Tips

**Tip 1:** Type `show mocks` in CLI to see what's fake vs real

**Tip 2:** All components are testable independently (run `.py` files)

**Tip 3:** Mock responses are in `adapters/llm/mock_llm.py` (easy to customize)

**Tip 4:** Test data is in `demo/mock_data.py` (change to your data)

**Tip 5:** Read `MOCKS.md` before swapping to real services

---

## 🎉 Success!

You now have a **complete, testable, mock-first thin slice** that:

✅ Validates the entire architecture  
✅ Processes appointments end-to-end  
✅ Costs $0 to run (all mocked)  
✅ Easy to demo to stakeholders  
✅ Clear path to production (swap mocks)  

**Ready to impress your team!** 🚀

---

## ❓ Questions?

- **"Why are decisions hardcoded?"** - It's mocked! Swap to LiteLLM for real AI decisions.
- **"Can I change the test data?"** - Yes! Edit `demo/mock_data.py`
- **"How long to production?"** - 2-3 weeks swapping mocks (see `MOCKS.md`)
- **"Is this secure?"** - Not yet. Add encryption & auth before production.
- **"What about other workflows?"** - This thin slice validates architecture. Easy to add more.

**Still stuck?** Check `README_THIN_SLICE.md` or `MOCKS.md`

---

**Go ahead, run the demo! 🎬**

```bash
python3 demo/cli.py
```




