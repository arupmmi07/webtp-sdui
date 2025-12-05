# ⚙️ Configuration Guide

Complete guide to configure timeouts, tokens, and other LLM settings.

---

## 📍 Where to Change Settings

### **Option 1: Environment Variables (.env file)** ⭐ RECOMMENDED

Edit `/Users/madhan.dhandapani/Documents/schedule/.env`:

```bash
# ============================================================
# LLM TIMEOUT SETTINGS
# ============================================================

# How long to wait for LLM response (seconds)
# Default: 120 (2 minutes)
# Increase if you get timeouts
LLM_REQUEST_TIMEOUT=180  # 3 minutes

# Connection timeout (seconds)
# Default: 30
LLM_CONNECTION_TIMEOUT=60


# ============================================================
# TOKEN SETTINGS
# ============================================================

# Max tokens for template orchestrator (main AI decision)
# Default: 4000
# Increase if responses are truncated
LLM_ORCHESTRATOR_MAX_TOKENS=6000

# Max tokens for scheduling agent
# Default: 2000
LLM_SCHEDULING_MAX_TOKENS=3000

# Max tokens for patient messages
# Default: 1000
LLM_ENGAGEMENT_MAX_TOKENS=1500


# ============================================================
# TEMPERATURE SETTINGS (0.0 = deterministic, 1.0 = creative)
# ============================================================

# Temperature for orchestrator (decision-making)
# Default: 0.3 (fairly deterministic)
LLM_ORCHESTRATOR_TEMPERATURE=0.3

# Temperature for scheduling (matching logic)
# Default: 0.2 (very deterministic)
LLM_SCHEDULING_TEMPERATURE=0.2

# Temperature for patient messages (more creative)
# Default: 0.7
LLM_ENGAGEMENT_TEMPERATURE=0.7


# ============================================================
# RETRY SETTINGS
# ============================================================

# Number of retries on failure
# Default: 3
LLM_MAX_RETRIES=5

# Delay between retries (seconds)
# Default: 2
LLM_RETRY_DELAY=3


# ============================================================
# FALLBACK SETTINGS
# ============================================================

# Enable automatic fallback to rule-based on LLM failure
# Default: true
LLM_ENABLE_FALLBACK=true

# Threshold score for auto-assignment (0-100)
# Default: 60
LLM_AUTO_ASSIGN_THRESHOLD=60


# ============================================================
# DEBUG SETTINGS
# ============================================================

# Enable debug logging
# Default: false
LLM_DEBUG=true

# Log full prompts and responses
# Default: false
LLM_LOG_PROMPTS=true
```

**After editing .env, restart services:**
```bash
make restart
```

---

### **Option 2: LiteLLM Proxy Settings**

Edit `/Users/madhan.dhandapani/Documents/schedule/config/litellm_config.yaml`:

```yaml
litellm_settings:
  # Retry & Timeout
  num_retries: 3
  request_timeout: 600  # ← CHANGE THIS (seconds)
  
  # Example: 20 minutes timeout
  # request_timeout: 1200
```

**After editing, restart LiteLLM:**
```bash
docker-compose restart litellm
```

---

### **Option 3: Python Config File**

Edit `/Users/madhan.dhandapani/Documents/schedule/config/llm_settings.py`:

```python
class LLMSettings:
    # Direct values (no env var fallback)
    REQUEST_TIMEOUT = 180  # 3 minutes
    ORCHESTRATOR_MAX_TOKENS = 6000
    # ... etc
```

**After editing, restart services:**
```bash
make restart
```

---

## 🎯 Common Scenarios

### **Scenario 1: LLM Responses are Slow/Timing Out**

**Solution: Increase timeout**

```bash
# In .env
LLM_REQUEST_TIMEOUT=300  # 5 minutes
```

```yaml
# In litellm_config.yaml
request_timeout: 1200  # 20 minutes
```

Then:
```bash
make restart
docker-compose restart litellm
```

---

### **Scenario 2: LLM Responses are Truncated**

**Solution: Increase max tokens**

```bash
# In .env
LLM_ORCHESTRATOR_MAX_TOKENS=8000  # Double it
```

Then:
```bash
make restart
```

---

### **Scenario 3: Want More Deterministic Results**

**Solution: Lower temperature**

```bash
# In .env
LLM_ORCHESTRATOR_TEMPERATURE=0.1  # Very deterministic
LLM_SCHEDULING_TEMPERATURE=0.0    # Completely deterministic
```

Then:
```bash
make restart
```

---

### **Scenario 4: Want More Creative Patient Messages**

**Solution: Increase engagement temperature**

```bash
# In .env
LLM_ENGAGEMENT_TEMPERATURE=0.9  # More creative
```

Then:
```bash
make restart
```

---

### **Scenario 5: Disable Fallback (Always Use LLM)**

**Solution: Disable fallback**

```bash
# In .env
LLM_ENABLE_FALLBACK=false
```

Then:
```bash
make restart
```

**Warning:** System will fail if LLM fails!

---

## 📊 View Current Settings

### **Check Current Configuration:**

```bash
# Run Python to see all settings
python -c "from config.llm_settings import LLMSettings; LLMSettings.print_settings()"
```

**Output:**
```json
{
  "timeouts": {
    "request_timeout": 120,
    "connection_timeout": 30
  },
  "tokens": {
    "orchestrator_max_tokens": 4000,
    "scheduling_max_tokens": 2000,
    "engagement_max_tokens": 1000
  },
  ...
}
```

---

## 🔍 Test Your Changes

### **1. Check if settings are loaded:**

```bash
tail -f logs/api.log | grep "LLM CONFIGURATION"
```

### **2. Trigger a workflow:**

```bash
# Open browser
open http://localhost:8000/schedule.html

# Click "Mark Unavailable"
# Watch logs:
tail -f logs/api.log
```

### **3. Check timeout:**

Look for lines like:
```
[LLM] Making assignment decisions...
[LLM] Request timeout: 180 seconds  ← Your new setting
```

---

## 📋 Configuration Priority

Settings are loaded in this order (last one wins):

1. **Default values** in `config/llm_settings.py`
2. **Environment variables** from `.env` file
3. **Runtime overrides** (if any)

**Example:**
```python
# Default in llm_settings.py
REQUEST_TIMEOUT = 120

# Override in .env
LLM_REQUEST_TIMEOUT=300

# Final value used: 300 ✅
```

---

## 🚀 Quick Reference

| Setting | Default | Where to Change | When to Restart |
|---------|---------|-----------------|-----------------|
| Request Timeout | 120s | `.env` → `LLM_REQUEST_TIMEOUT` | `make restart` |
| Max Tokens | 4000 | `.env` → `LLM_ORCHESTRATOR_MAX_TOKENS` | `make restart` |
| Temperature | 0.3 | `.env` → `LLM_ORCHESTRATOR_TEMPERATURE` | `make restart` |
| LiteLLM Timeout | 600s | `litellm_config.yaml` → `request_timeout` | `docker-compose restart litellm` |
| Fallback | true | `.env` → `LLM_ENABLE_FALLBACK` | `make restart` |
| Debug Logs | false | `.env` → `LLM_DEBUG` | `make restart` |

---

## 💡 Best Practices

### **Production Settings:**
```bash
LLM_REQUEST_TIMEOUT=300        # 5 min (handle slow models)
LLM_ORCHESTRATOR_MAX_TOKENS=6000  # Avoid truncation
LLM_ORCHESTRATOR_TEMPERATURE=0.2  # Consistent results
LLM_ENABLE_FALLBACK=true       # Always have backup
LLM_MAX_RETRIES=5              # Handle transient failures
```

### **Development Settings:**
```bash
LLM_REQUEST_TIMEOUT=60         # Fail fast
LLM_DEBUG=true                 # See what's happening
LLM_LOG_PROMPTS=true           # Debug prompts
LLM_ENABLE_FALLBACK=true       # Test both paths
```

### **Demo Settings:**
```bash
LLM_REQUEST_TIMEOUT=120        # Not too long for demos
LLM_ORCHESTRATOR_TEMPERATURE=0.3  # Predictable but varied
LLM_ENABLE_FALLBACK=true       # Always works
LLM_DEBUG=false                # Clean logs
```

---

## ⚠️ Troubleshooting

### **Settings not taking effect:**

1. **Check .env file exists:**
   ```bash
   ls -la .env
   ```

2. **Check env vars are loaded:**
   ```bash
   python -c "import os; print(os.getenv('LLM_REQUEST_TIMEOUT'))"
   ```

3. **Restart services:**
   ```bash
   make restart
   docker-compose restart litellm
   ```

### **Still timing out:**

1. **Check LM Studio is running:**
   ```bash
   curl http://localhost:1234/v1/models
   ```

2. **Test direct call:**
   ```bash
   curl -X POST http://localhost:1234/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model":"gpt-oss-20b","messages":[{"role":"user","content":"Hello"}]}'
   ```

3. **Check LiteLLM logs:**
   ```bash
   docker logs healthcare-litellm --tail 50
   ```

---

## 📚 Related Documentation

- [LiteLLM Configuration](../config/litellm_config.yaml)
- [Environment Variables](.env)
- [LLM Settings](../config/llm_settings.py)
- [API Documentation](http://localhost:8000/docs)
- [LiteLLM UI](http://localhost:4000/ui)

---

**Questions? Check logs:**
```bash
tail -f logs/api.log
docker logs healthcare-litellm --tail 100
```

