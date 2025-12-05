# 🖥️ LM Studio + LiteLLM Integration

Use **free local models** with LM Studio for testing - **$0 cost!**

---

## 🎯 Why Use LM Studio?

✅ **FREE** - No API costs  
✅ **Private** - Data stays on your machine  
✅ **Fast** - No network latency (if you have good GPU)  
✅ **Unlimited** - No rate limits or budget caps  
✅ **Offline** - Works without internet  

Perfect for:
- 💻 Development & testing
- 🧪 Experimentation
- 📚 Learning the system
- 🔒 Privacy-sensitive demos

---

## 📦 Step 1: Install LM Studio

### Download
1. Go to: https://lmstudio.ai/
2. Download for your OS (Mac/Windows/Linux)
3. Install and open LM Studio

### Recommended Models

For **best results** with this healthcare app:

| Model | Size | Quality | Speed | Download |
|-------|------|---------|-------|----------|
| **Llama 3.1 8B** | ~5GB | ⭐⭐⭐⭐ | Fast | Recommended |
| **Mistral 7B** | ~4GB | ⭐⭐⭐ | Very Fast | Good |
| **Phi-3 Medium** | ~8GB | ⭐⭐⭐⭐ | Fast | Good |
| **Llama 3.1 70B** | ~40GB | ⭐⭐⭐⭐⭐ | Slow | Best (if you have GPU) |

**To download:**
1. Click "🔍 Search" in LM Studio
2. Search for "Llama 3.1 8B" or "Mistral 7B"
3. Click "Download"
4. Wait for download to complete

---

## 🚀 Step 2: Start LM Studio Server

### 2.1 Load a Model
1. Go to "💬 Chat" tab in LM Studio
2. Select your downloaded model from dropdown
3. Wait for model to load (shows "Ready" when done)

### 2.2 Start Server
1. Go to "🔌 Local Server" tab
2. Click "Start Server"
3. Server should start on: `http://localhost:1234`
4. You'll see: ✅ "Server running on port 1234"

**Important Settings:**
- Port: `1234` (default - keep this)
- CORS: Enable "Allow CORS"
- API: OpenAI-compatible

---

## 🐳 Step 3: Connect Docker to LM Studio

### Update Environment

Edit your `.env` file:

```bash
# .env
USE_MOCK_LLM=false
USE_LOCAL_MODEL=true
LITELLM_DEFAULT_MODEL=local-llama

# You can leave these empty when using local models
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
```

### Start Docker Services

```bash
# Start with local model
make docker-up

# Check logs
make docker-logs
```

---

## 🧪 Step 4: Test It

### Test 1: Via UI

1. Open UI: http://localhost:8501
2. Type: `therapist departed T001`
3. Watch it use your local model!

You should see in logs:
```
[LiteLLM] Using local-llama
[LM Studio] Request received
```

### Test 2: Via API

```bash
# Test LiteLLM connection
curl http://localhost:4000/health

# Test model list
curl http://localhost:4000/models

# Test chat completion
curl -X POST http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "local-llama",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

---

## ⚙️ Configuration Options

### Use Local Model as Primary

Edit `config/litellm_config.yaml`:

```yaml
router_settings:
  model_group_alias:
    production: ["local-llama", "claude-sonnet-4"]  # Try local first
```

### Use Local Model as Fallback

```yaml
fallbacks:
  - ["claude-sonnet-4", "local-llama"]  # Use local if Claude fails
```

### Mixed Strategy (Recommended for Dev)

```yaml
router_settings:
  model_group_alias:
    dev: ["local-llama", "claude-haiku-3.5"]  # Local first, then cheap API
```

---

## 🔧 Troubleshooting

### Issue: "Connection refused to localhost:1234"

**Solution:**
```bash
# Check if LM Studio server is running
curl http://localhost:1234/v1/models

# If error, go to LM Studio:
1. Click "Local Server" tab
2. Click "Start Server"
3. Wait for "Server running" message
```

### Issue: "Docker can't connect to host.docker.internal"

**Mac/Windows:** Should work automatically

**Linux:**
```bash
# Edit docker-compose.yml
# Replace: http://host.docker.internal:1234
# With: http://172.17.0.1:1234
```

### Issue: Model responses are slow/bad quality

**Solutions:**
1. **Use smaller model** (Mistral 7B instead of Llama 70B)
2. **Close other apps** to free up RAM/GPU
3. **Increase context length** in LM Studio settings
4. **Try different model** - some models better for structured tasks

### Issue: "Model not found"

**Solution:**
```bash
# Check what model is loaded in LM Studio
# The model name in LiteLLM doesn't matter
# LM Studio uses whatever model is currently loaded

# Or specify exact model:
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama-3.1-8b",
    "messages": [...]
  }'
```

---

## 💡 Performance Tips

### For Best Results

1. **GPU Acceleration**
   - LM Studio auto-detects GPU
   - Check "GPU Layers" slider in LM Studio
   - More layers = faster (if you have VRAM)

2. **Model Selection**
   - **Llama 3.1 8B**: Best balance
   - **Mistral 7B**: Faster, good quality
   - **Phi-3**: Very fast, good for simple tasks

3. **Context Window**
   - Set to 4096 or 8192 tokens
   - Higher = better but slower

4. **Temperature**
   - 0.1-0.3: More consistent (good for production)
   - 0.7: Balanced (default)
   - 0.9+: More creative (good for exploring)

---

## 📊 Cost Comparison

### Local Model (LM Studio)
```
Setup:          One-time (download model)
Cost per call:  $0.00
Monthly cost:   $0.00
Hardware:       Your computer
Speed:          Fast (with GPU) / Slow (CPU only)
Privacy:        100% private
```

### Cloud API (Anthropic)
```
Setup:          Get API key
Cost per call:  ~$0.03
Monthly cost:   $50-150 (with $5/day limit)
Hardware:       None needed
Speed:          Very fast
Privacy:        Data sent to Anthropic
```

### Recommended Strategy

**Development/Testing:**
```yaml
USE_LOCAL_MODEL=true
# Use LM Studio - FREE!
```

**Staging:**
```yaml
USE_LOCAL_MODEL=false
LITELLM_DEFAULT_MODEL=claude-haiku-3.5
# Use cheap API - ~$10-20/month
```

**Production:**
```yaml
USE_LOCAL_MODEL=false
LITELLM_DEFAULT_MODEL=claude-sonnet-4
fallback: ["claude-sonnet-4", "local-llama"]
# Use best API with local fallback
```

---

## 🔄 Switching Between Local and Cloud

### Switch to Local
```bash
# .env
USE_MOCK_LLM=false
USE_LOCAL_MODEL=true
LITELLM_DEFAULT_MODEL=local-llama

make docker-restart
```

### Switch to Cloud
```bash
# .env
USE_MOCK_LLM=false
USE_LOCAL_MODEL=false
LITELLM_DEFAULT_MODEL=claude-sonnet-4
ANTHROPIC_API_KEY=sk-ant-api03-...

make docker-restart
```

### Use Both (Hybrid)
```bash
# .env
USE_MOCK_LLM=false
USE_LOCAL_MODEL=true
LITELLM_DEFAULT_MODEL=local-llama
ANTHROPIC_API_KEY=sk-ant-api03-...

# config/litellm_config.yaml
fallbacks:
  - ["local-llama", "claude-sonnet-4"]
# Try local first, fall back to cloud if needed
```

---

## 📚 Resources

- **LM Studio Docs**: https://lmstudio.ai/docs
- **Model Hub**: https://huggingface.co/models
- **LiteLLM + Local**: https://docs.litellm.ai/docs/providers/openai_compatible

---

## ✅ Quick Setup Checklist

- [ ] Download LM Studio
- [ ] Download a model (Llama 3.1 8B recommended)
- [ ] Start LM Studio server (port 1234)
- [ ] Edit `.env`: `USE_LOCAL_MODEL=true`
- [ ] Run: `make docker-up`
- [ ] Test: Visit http://localhost:8501
- [ ] Type: `therapist departed T001`
- [ ] Verify: Check logs for "local-llama"

---

## 🎉 Done!

You're now running the entire system **locally and for FREE**!

**No API costs. No rate limits. Complete privacy.** 🔒💰

