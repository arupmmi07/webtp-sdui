# LLM Configuration Fix

## Problem
When running `make dev` and triggering "Mark Unavailable" workflow, the system was falling back to rule-based templates instead of using the LLM (LM Studio).

**Error in logs:**
```
[EMAIL] Warning: LangFuse prompt/LLM call failed: litellm.InternalServerError: InternalServerError: OpenAIException - Connection error.
[EMAIL] Falling back to template
```

## Root Cause
The application wasn't configured to connect to LM Studio. The `SmartSchedulingAgent` requires these environment variables:
- `LITELLM_BASE_URL`
- `LITELLM_API_KEY`
- `LITELLM_DEFAULT_MODEL`

Without these, the agent falls back to `MockLLM` (rule-based).

## Solution
Updated `/scripts/start.sh` to automatically export LM Studio environment variables when running `make dev`:

```bash
# Export LiteLLM environment variables for LM Studio
export LITELLM_BASE_URL="http://localhost:1234/v1"
export LITELLM_API_KEY="lm-studio"
export LITELLM_DEFAULT_MODEL="openai/gpt-oss-20b"
export USE_MOCK_LLM="false"
```

## How It Works Now

### 1. Run `make dev`
```bash
make dev
```

**What happens:**
- ✅ Kills existing processes on ports 8000 & 8501
- ✅ Exports LM Studio environment variables
- ✅ Starts API server with LLM enabled
- ✅ Starts UI with LLM enabled

**Output:**
```
🤖 LLM Configuration:
   Provider: LM Studio (Local)
   Model: openai/gpt-oss-20b
   API: http://localhost:1234/v1
```

### 2. Agents Auto-Configure
When you trigger a workflow (e.g., "Mark Unavailable"):

**SmartSchedulingAgent:**
```python
# In agents/smart_scheduling_agent.py (lines 68-92)
litellm_base_url = os.getenv("LITELLM_BASE_URL")      # ✅ Set by start.sh
litellm_api_key = os.getenv("LITELLM_API_KEY")        # ✅ Set by start.sh
default_model = os.getenv("LITELLM_DEFAULT_MODEL")    # ✅ Set by start.sh

if litellm_base_url and litellm_api_key and default_model:
    self.llm = LiteLLMAdapter(
        model=default_model,
        api_base=litellm_base_url,
        api_key=litellm_api_key
    )
    llm_type = f"Real LLM ({default_model})"
else:
    # Fallback to Mock
    self.llm = MockLLM()
```

### 3. LLM Calls Work
Now when you mark a provider unavailable:
- ✅ LLM generates personalized emails
- ✅ LLM performs intelligent provider matching
- ✅ No more "Falling back to template" errors

## Verification

### Check LM Studio is Running
```bash
curl http://localhost:1234/v1/models
```

**Expected output:**
```json
{
  "data": [
    {
      "id": "openai/gpt-oss-20b",
      "object": "model",
      "owned_by": "organization_owner"
    }
  ]
}
```

### Check Services are Running
```bash
make status
```

### Test Workflow
1. Open: http://localhost:8000/schedule.html
2. Click "🚫 Mark Unavailable" on Dr. Sarah Johnson
3. Check logs: `tail -f logs/api.log`
4. Should see: `[AGENT] LLM: Real LLM (openai/gpt-oss-20b)`

## Prerequisites
- ✅ LM Studio must be running
- ✅ Model `openai/gpt-oss-20b` must be loaded in LM Studio
- ✅ LM Studio server must be started on port 1234

## Troubleshooting

### If LLM still falls back to rules:
1. **Check LM Studio is running:**
   ```bash
   ps aux | grep -i "LM Studio"
   ```

2. **Check LM Studio API is accessible:**
   ```bash
   curl http://localhost:1234/v1/models
   ```

3. **Verify model is loaded:**
   - Open LM Studio
   - Go to "Local Server" tab
   - Check "openai/gpt-oss-20b" is loaded and server is running

4. **Restart services:**
   ```bash
   make stop
   make dev
   ```

5. **Check environment variables are set:**
   ```bash
   tail -10 logs/api.log | grep "LLM Configuration"
   ```
   Should show:
   ```
   🤖 LLM Configuration:
      Provider: LM Studio (Local)
      Model: openai/gpt-oss-20b
   ```

### Alternative: Use Cloud API (Anthropic/OpenAI)
If you want to use cloud APIs instead of LM Studio, edit `scripts/start.sh`:

```bash
# For Anthropic Claude
export LITELLM_BASE_URL="https://api.anthropic.com"
export LITELLM_API_KEY="your-anthropic-api-key"
export LITELLM_DEFAULT_MODEL="claude-sonnet-4"

# For OpenAI GPT
export LITELLM_BASE_URL="https://api.openai.com/v1"
export LITELLM_API_KEY="your-openai-api-key"
export LITELLM_DEFAULT_MODEL="gpt-4o"
```

## Summary
**One command does it all:**
```bash
make dev
```

✅ Kills existing ports  
✅ Configures LM Studio automatically  
✅ Starts services with LLM enabled  
✅ Ready to use AI-powered workflows  

**No manual configuration needed!**

