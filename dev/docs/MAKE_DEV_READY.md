# ✅ `make dev` - ONE COMMAND SETUP

## Summary
**You can now just run `make dev` and everything works!**

## What Was Fixed

### Problem
When running `make dev` → marking provider unavailable → system used **rule-based fallback** instead of **LLM**.

### Root Cause
Agents weren't configured to connect to LM Studio automatically.

### Solution
Updated 4 files to enable LLM by default:

1. **`scripts/start.sh`** - Exports LM Studio env vars automatically
2. **`agents/smart_scheduling_agent.py`** - Defaults to LM Studio
3. **`agents/patient_engagement_agent.py`** - Defaults to LM Studio  
4. **`config/llm_settings.py`** - Defaults to LM Studio

## How to Use

### 1. Start LM Studio
- Open LM Studio app
- Load model: `openai/gpt-oss-20b`
- Start Local Server (port 1234)

### 2. Run One Command
```bash
make dev
```

**That's it!** ✨

## What `make dev` Does

1. ✅ **Kills existing processes** on ports 8000 & 8501
2. ✅ **Resets demo data** to initial state
3. ✅ **Exports LM Studio config** automatically:
   ```bash
   export LITELLM_BASE_URL="http://localhost:1234/v1"
   export LITELLM_API_KEY="lm-studio"
   export LITELLM_DEFAULT_MODEL="openai/gpt-oss-20b"
   ```
4. ✅ **Starts API & UI** with LLM enabled

## Verification

### You'll see this output:
```
🤖 LLM Configuration:
   Provider: LM Studio (Local)
   Model: openai/gpt-oss-20b
   API: http://localhost:1234/v1

✅ API server started (PID: xxxxx)
   URL: http://localhost:8000

✅ Streamlit UI started (PID: xxxxx)
   URL: http://localhost:8501
```

### Test the workflow:
1. Open: http://localhost:8000/schedule.html
2. Click **"🚫 Mark Unavailable"** on Dr. Sarah Johnson
3. Watch the magic:
   - ✅ LLM generates **personalized emails**
   - ✅ LLM performs **intelligent provider matching**
   - ✅ **NO** "Falling back to template" errors

## Fallback Behavior

If LM Studio is **not running**, agents will gracefully fall back to MockLLM and show:
```
[AGENT] Warning: LiteLLM configuration failed
[AGENT] Falling back to Mock LLM
```

To fix: Just start LM Studio and restart services (`make dev`).

## Files Modified

| File | Change |
|------|--------|
| `scripts/start.sh` | Added LM Studio env var exports |
| `agents/smart_scheduling_agent.py` | Changed default from no config → LM Studio |
| `agents/patient_engagement_agent.py` | Changed default from `localhost:4000` → `localhost:1234/v1` |
| `config/llm_settings.py` | Changed default from `localhost:4000` → `localhost:1234/v1` |

## Architecture

```
┌─────────────────────────────────────────────────┐
│  make dev                                       │
│  └─ scripts/start.sh                            │
│     ├─ Export LITELLM_BASE_URL, API_KEY, MODEL  │
│     ├─ Kill ports 8000, 8501                    │
│     └─ Start API & UI servers                   │
└─────────────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────┐
│  agents/smart_scheduling_agent.py               │
│  agents/patient_engagement_agent.py             │
│  └─ Read env vars (or use LM Studio defaults)  │
│     └─ Initialize LiteLLMAdapter                │
│        └─ Connect to http://localhost:1234/v1   │
└─────────────────────────────────────────────────┘
                   │
                   ↓
┌─────────────────────────────────────────────────┐
│  LM Studio (Local LLM Server)                   │
│  └─ Model: openai/gpt-oss-20b                   │
│     └─ API: http://localhost:1234/v1            │
└─────────────────────────────────────────────────┘
```

## No More Manual Setup! 🎉

Before:
- ❌ Export env vars manually
- ❌ Configure each agent separately
- ❌ Remember to kill ports
- ❌ 5+ steps to get started

After:
- ✅ **ONE COMMAND: `make dev`**
- ✅ Everything configured automatically
- ✅ Ready to demo in seconds

---

**Remember:** Just run `make dev` - that's it! 🚀

