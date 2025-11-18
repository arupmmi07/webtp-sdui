# LiteLLM + LangFuse Setup Guide

## Overview

This system uses **LiteLLM** as an LLM gateway and **LangFuse** for observability, providing:
- Zero vendor lock-in (swap providers instantly)
- Automatic fallbacks (if Claude fails, auto-switch to GPT-4)
- Prompt versioning without code deploys
- Complete tracing and cost tracking

## Architecture

```
Your Code
    ↓
LangFuse (tracks everything)
    ↓
LiteLLM (routes to best provider)
    ↓
Claude / GPT-4 / Gemini / etc.
```

## Quick Start

### 1. Get API Keys

```bash
# LangFuse (free tier available)
# Sign up at: https://cloud.langfuse.com
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."

# LLM Providers (get at least one)
export ANTHROPIC_API_KEY="sk-ant-..."      # Primary
export OPENAI_API_KEY="sk-..."             # Fallback
export GEMINI_API_KEY="..."                # Fallback
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your keys
nano .env
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Test the Setup

```python
from adapters.llm import LiteLLMAdapter

# Initialize (automatically uses LangFuse)
llm = LiteLLMAdapter(
    model="claude-sonnet",
    enable_langfuse=True
)

# Make a call (traced in LangFuse, auto-fallback if needed)
response = llm.generate(
    prompt="Hello, how are you?",
    metadata={
        "session_id": "test-session",
        "user_id": "admin"
    }
)

print(response.content)

# Flush traces to LangFuse
llm.flush_langfuse()
```

## Features

### 1. Automatic Fallbacks

```yaml
# config/litellm_config.yaml
fallbacks:
  - claude-sonnet    # Try first
  - gpt-4-fallback   # If Claude fails
  - gemini-fallback  # If both fail
```

If Claude is down or rate-limited, LiteLLM automatically switches to GPT-4, then Gemini.

### 2. Prompt Management in LangFuse

**Instead of hardcoding prompts:**
```python
# ❌ OLD WAY (hardcoded in code)
system_prompt = "You are a helpful assistant..."
```

**Use LangFuse prompt management:**
```python
# ✅ NEW WAY (managed in LangFuse UI)
system_prompt = llm.get_prompt(
    prompt_name="therapist-replacement-orchestrator-v1",
    variables={"max_appointments": 15}
)
```

**Benefits:**
- Update prompts without code deployment
- A/B test different prompt versions
- Track which prompts perform best
- Version history and rollback

### 3. Complete Tracing

Every LLM call is automatically traced in LangFuse with:
- Input (prompt, system message)
- Output (response, tokens)
- Metadata (session_id, user_id, tags)
- Timing (latency)
- Cost (per model)

**View in LangFuse Dashboard:**
```
Session: SESSION_2025-11-15_001
├── Trace 1: Trigger Handler
│   ├── Input: "Identify affected appointments for therapist T123"
│   ├── Output: "Found 15 appointments..."
│   ├── Latency: 1.2s
│   └── Cost: $0.003
├── Trace 2: Matching Agent
│   ├── Input: "Filter qualified providers for patient P001"
│   ├── Output: "3 qualified providers found..."
│   ├── Latency: 0.8s
│   └── Cost: $0.002
└── Total Session Cost: $0.015
```

### 4. Cost Tracking

LangFuse automatically tracks:
- Cost per LLM provider
- Cost per user/session
- Cost per agent
- Daily/weekly/monthly totals

**Example Dashboard:**
```
November 2025 Costs:
├── Claude Sonnet: $45.23 (85% of calls)
├── GPT-4: $8.12 (10% - fallbacks)
├── Gemini: $2.15 (5% - fallbacks)
└── Total: $55.50
```

### 5. Load Balancing

```yaml
# config/litellm_config.yaml
router_settings:
  routing_strategy: least-busy
  
model_list:
  # Multiple instances of same model
  - model_name: claude-sonnet-1
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: ${ANTHROPIC_API_KEY_1}
  
  - model_name: claude-sonnet-2
    litellm_params:
      model: anthropic/claude-sonnet-4
      api_key: ${ANTHROPIC_API_KEY_2}
```

LiteLLM automatically load balances between instances.

## Configuration Reference

### Environment-Specific Settings

```yaml
# config/litellm_config.yaml
environments:
  development:
    default_model: ollama-local  # Free, no API key
    langfuse:
      enabled: false  # Don't track dev calls
  
  staging:
    default_model: claude-sonnet
    langfuse:
      enabled: true
      default_tags: [staging]
  
  production:
    default_model: claude-sonnet
    fallbacks_enabled: true
    langfuse:
      enabled: true
      default_tags: [production]
```

Switch environments:
```bash
export ENVIRONMENT=production
```

### Rate Limiting

```yaml
router_settings:
  rpm: 500   # Max 500 requests per minute
  tpm: 100000  # Max 100k tokens per minute
```

Prevents hitting provider rate limits.

### Caching

```yaml
router_settings:
  cache:
    type: redis
    ttl: 3600  # Cache for 1 hour
```

Reduces costs by caching identical requests.

## LangFuse Features

### 1. Prompt Versioning

**In LangFuse UI:**
1. Go to "Prompts" → "Create Prompt"
2. Name: `smart-scheduling-matching-v1`
3. Content:
   ```
   You are the Smart Scheduling Agent. Your job is to find qualified 
   replacement therapists for affected appointments.
   
   Filters to apply:
   1. Required skills: {{required_skills}}
   2. POC authorization
   3. Payer compliance
   ...
   ```
4. Save and deploy

**In your code:**
```python
prompt = llm.get_prompt(
    "smart-scheduling-matching-v1",
    variables={"required_skills": "orthopedic"}
)
```

When you update the prompt in LangFuse UI, it updates everywhere instantly - no code deploy!

### 2. A/B Testing

Test two prompt versions:
```python
# 50% get version A, 50% get version B
prompt = llm.get_prompt(
    "smart-scheduling-matching",
    version="latest"  # LangFuse handles A/B split
)
```

Track which performs better in LangFuse analytics.

### 3. User & Session Tracking

```python
response = llm.generate(
    prompt="...",
    metadata={
        "user_id": "sarah.chen@clinic.com",
        "session_id": "SESSION_123",
        "tags": ["therapist-replacement", "urgent"]
    }
)
```

Filter traces in LangFuse by user, session, or tags.

## Common Patterns

### Pattern 1: Agent with Prompt from LangFuse

```python
class SmartSchedulingAgent:
    def __init__(self, llm: LiteLLMAdapter):
        self.llm = llm
        # Prompt managed in LangFuse
        self.system_prompt = llm.get_prompt("smart-scheduling-system-v1")
    
    def execute(self, appointment):
        response = self.llm.generate(
            prompt=f"Process appointment {appointment.id}",
            system=self.system_prompt,
            metadata={
                "session_id": appointment.session_id,
                "appointment_id": appointment.id
            }
        )
        return response
```

### Pattern 2: Multiple Models for Different Tasks

```python
# Use Claude for complex reasoning
claude = LiteLLMAdapter(model="claude-sonnet")

# Use GPT-4 for tool calling (better at tools)
gpt4 = LiteLLMAdapter(model="gpt-4-fallback")

# Complex reasoning task
analysis = claude.generate(prompt="Analyze this complex case...")

# Tool-heavy task
tool_result = gpt4.generate(
    prompt="Call these APIs...",
    tools=[...mcp_tools...]
)
```

### Pattern 3: Cost-Conscious Development

```python
import os

# Dev: Use free Ollama
# Prod: Use Claude
model = "ollama-local" if os.getenv("ENVIRONMENT") == "development" else "claude-sonnet"

llm = LiteLLMAdapter(
    model=model,
    enable_langfuse=(os.getenv("ENVIRONMENT") != "development")
)
```

## Monitoring & Alerts

### Set Up Alerts in LangFuse

1. Go to LangFuse → Settings → Alerts
2. Configure:
   - **Error Rate:** Alert if >5% of calls fail
   - **Latency:** Alert if avg latency >5s
   - **Cost:** Alert if daily cost >$100

### Check Metrics

```python
# At end of session
llm.flush_langfuse()

# View in LangFuse dashboard:
# - Total traces
# - Success rate
# - Average latency
# - Total cost
```

## Troubleshooting

### Issue: LangFuse not receiving traces

```bash
# Check env vars are set
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# Ensure flush is called
llm.flush_langfuse()

# Check LangFuse dashboard for API key validity
```

### Issue: Fallback not working

```bash
# Check config
cat config/litellm_config.yaml

# Ensure fallback API keys are set
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY

# Test fallback manually
python -c "from adapters.llm import LiteLLMAdapter; llm = LiteLLMAdapter(model='gpt-4-fallback'); print(llm.generate('test'))"
```

### Issue: High costs

1. Check LangFuse cost dashboard
2. Identify expensive calls
3. Options:
   - Enable caching
   - Use smaller models for simple tasks
   - Reduce token limits

## Best Practices

### 1. Always Use Metadata

```python
response = llm.generate(
    prompt="...",
    metadata={
        "session_id": session_id,      # Track session
        "user_id": user_id,            # Track user
        "agent": "smart_scheduling",   # Track which agent
        "stage": "filtering",          # Track workflow stage
        "tags": ["urgent", "medicare"] # Filter in LangFuse
    }
)
```

### 2. Manage Prompts in LangFuse

- ✅ Store all system prompts in LangFuse
- ✅ Version prompts (v1, v2, v3)
- ✅ Test new versions before deploying
- ❌ Don't hardcode prompts in code

### 3. Monitor Costs Daily

- Check LangFuse dashboard daily
- Set up cost alerts
- Review expensive calls
- Optimize where needed

### 4. Use Appropriate Models

```python
# Complex reasoning: Use Claude
claude = LiteLLMAdapter(model="claude-sonnet")

# Simple classification: Use cheaper model
gpt3 = LiteLLMAdapter(model="gpt-3.5-turbo")

# Development: Use free Ollama
ollama = LiteLLMAdapter(model="ollama-local")
```

## Production Checklist

- [ ] All API keys configured in production environment
- [ ] LangFuse project created and keys configured
- [ ] Fallback models configured and tested
- [ ] Cost alerts set up in LangFuse
- [ ] Prompts migrated to LangFuse prompt management
- [ ] Rate limiting configured
- [ ] Caching enabled (if using Redis)
- [ ] Monitoring dashboard reviewed daily
- [ ] Team trained on LangFuse UI

## Resources

- **LiteLLM Docs:** https://docs.litellm.ai
- **LangFuse Docs:** https://langfuse.com/docs
- **LangFuse Cloud:** https://cloud.langfuse.com
- **Our Config:** `config/litellm_config.yaml`
- **Our Adapter:** `adapters/llm/litellm_adapter.py`




