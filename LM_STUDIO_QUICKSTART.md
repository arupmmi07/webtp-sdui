# 🚀 LM Studio Quick Start - GPT-OSS-20B

Test with **GPT-OSS-20B** model for FREE!

---

## Step-by-Step Setup (10 minutes)

### 1. Download & Install LM Studio

```bash
# Open browser
open https://lmstudio.ai

# Download for your OS and install
```

### 2. Download GPT-OSS-20B Model

In LM Studio:
1. Click **"🔍 Search"** tab
2. Search for: **"gpt-oss-20b"** or **"GPT"**
3. Look for models like:
   - `gpt-oss-20b-instruct-gguf`
   - `GPT-NeoX-20B`
   - Similar 20B parameter models
4. Click **"Download"**
5. Wait for download to complete (~12GB)

**Alternative models to try:**
- `meta-llama/Llama-3.1-8B-Instruct` (recommended, ~5GB)
- `mistralai/Mistral-7B-Instruct-v0.2` (fast, ~4GB)
- `microsoft/Phi-3-medium-4k-instruct` (~8GB)

### 3. Load Model in LM Studio

1. Go to **"💬 Chat"** tab
2. Select your downloaded model from dropdown
3. Wait for "Ready ✅" status

### 4. Start LM Studio Server

1. Go to **"🔌 Local Server"** tab
2. **Port**: Make sure it's `1234` (default)
3. **CORS**: Enable "Allow CORS"
4. Click **"Start Server"**
5. You should see: ✅ **"Server running on port 1234"**

---

## Configure Healthcare App

### Update Environment

```bash
# Run setup script
bash scripts/setup-env.sh

# Edit .env file
nano .env
```

Change these lines in `.env`:
```bash
USE_MOCK_LLM=false
USE_LOCAL_MODEL=true
LITELLM_DEFAULT_MODEL=gpt-oss-20b
```

### Start Services

```bash
# Start Docker services
make docker-up

# Wait for all services to start (~30 seconds)
```

---

## Test the Integration

### Quick Test Script

```bash
# Run automated test
./test_lm_studio.sh
```

This will check:
- ✅ LM Studio server is running
- ✅ Model is loaded and responding
- ✅ LiteLLM can connect to LM Studio
- ✅ API and UI are running

### Manual Test

```bash
# Test LM Studio directly
curl -X POST http://localhost:1234/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss-20b",
    "messages": [{"role": "user", "content": "Say hello"}],
    "temperature": 0.7
  }'
```

Expected response:
```json
{
  "choices": [
    {
      "message": {
        "content": "Hello! How can I help you today?"
      }
    }
  ]
}
```

### Test via UI

1. Open: http://localhost:8501
2. Type: `therapist departed T001`
3. Watch the workflow execute using your local model!

You should see in Docker logs:
```
[LiteLLM] Using model: gpt-oss-20b
[LM Studio] Request received
[Agent] Filtering providers...
```

---

## Verify It's Working

### Check Docker Logs

```bash
# View logs from all services
make docker-logs

# Or view specific service
docker-compose logs -f litellm
docker-compose logs -f api
```

Look for:
```
[LiteLLM] Model: gpt-oss-20b
[LiteLLM] API Base: http://host.docker.internal:1234/v1
[LM Studio] Processing request...
```

### Check LM Studio Logs

In LM Studio "Local Server" tab, you should see:
```
POST /v1/chat/completions
Status: 200 OK
Tokens: 150
```

---

## Common Issues & Solutions

### Issue 1: "Connection refused to localhost:1234"

**Solution:**
```bash
# Make sure LM Studio server is started
# Go to LM Studio → Local Server → Start Server

# Test connection
curl http://localhost:1234/v1/models
```

### Issue 2: "Model not loaded"

**Solution:**
1. Go to LM Studio → Chat tab
2. Select your model from dropdown
3. Wait for "Ready ✅" message
4. Then start server

### Issue 3: "host.docker.internal not found" (Linux)

**Solution:**
Edit `config/litellm_config.yaml`:
```yaml
api_base: http://172.17.0.1:1234/v1  # Instead of host.docker.internal
```

Then restart:
```bash
docker-compose restart litellm
```

### Issue 4: Slow responses

**Solutions:**
- Use GPU acceleration (check LM Studio settings)
- Use smaller model (Mistral 7B instead of 20B)
- Reduce max_tokens in config
- Close other applications

### Issue 5: Out of memory

**Solutions:**
- Use quantized model (Q4 or Q5 instead of FP16)
- Use smaller model (8B instead of 20B)
- Close other applications
- Reduce GPU layers in LM Studio

---

## Model Recommendations

| Model | Size | Quality | Speed | Best For |
|-------|------|---------|-------|----------|
| **GPT-OSS-20B** | ~12GB | ⭐⭐⭐⭐⭐ | Medium | Complex reasoning |
| **Llama 3.1 8B** | ~5GB | ⭐⭐⭐⭐ | Fast | **Recommended** |
| **Mistral 7B** | ~4GB | ⭐⭐⭐ | Very Fast | Quick tests |
| **Phi-3 Medium** | ~8GB | ⭐⭐⭐⭐ | Fast | Good balance |

**For this healthcare app:**
- **Development**: Llama 3.1 8B or Mistral 7B (fast iteration)
- **Testing**: GPT-OSS-20B (if you have good hardware)
- **Production**: Claude Sonnet 4 (cloud API for best quality)

---

## Configuration Options

### Use GPT-OSS-20B as Primary

Edit `.env`:
```bash
LITELLM_DEFAULT_MODEL=gpt-oss-20b
```

### Use as Fallback (Hybrid Mode)

Edit `config/litellm_config.yaml`:
```yaml
fallbacks:
  - ["claude-sonnet-4", "gpt-oss-20b"]  # Use local if cloud fails
```

Set in `.env`:
```bash
USE_LOCAL_MODEL=true
ANTHROPIC_API_KEY=sk-ant-api03-...  # Your cloud API key
```

This gives you:
- ✅ Best quality (Claude)
- ✅ Zero cost fallback (local model)
- ✅ No downtime if API fails

---

## Performance Tuning

### In LM Studio

1. **GPU Layers**: Set to maximum (if you have GPU)
2. **Context Length**: 4096 or 8192
3. **Batch Size**: 512 (default)
4. **Threads**: Use all CPU cores

### In `config/litellm_config.yaml`

```yaml
- model_name: gpt-oss-20b
  litellm_params:
    model: openai/gpt-oss-20b
    api_base: http://host.docker.internal:1234/v1
    api_key: "lm-studio"
    max_tokens: 2048  # Reduce for faster responses
    temperature: 0.3  # Lower = more consistent
```

---

## Monitoring

### Check Requests in Real-Time

```bash
# Terminal 1: Watch LM Studio logs
# (in LM Studio app)

# Terminal 2: Watch LiteLLM logs
docker-compose logs -f litellm

# Terminal 3: Watch API logs
docker-compose logs -f api
```

### Check Performance

In LM Studio "Local Server" tab:
- **Requests**: Total requests processed
- **Avg Response Time**: ~2-5 seconds is good
- **Tokens/sec**: Higher = faster

---

## Cost Savings

### Local Model (LM Studio)
```
Per workflow:    $0.00
Per day:         $0.00
Per month:       $0.00
Total savings:   100%
```

### vs Cloud API
```
Per workflow:    $0.035
100/day:         $3.50/day = $105/month
Savings:         $105/month by using local!
```

**When to use local:**
- Development & testing
- Low-stakes demos
- Privacy-sensitive data
- Learning the system

**When to use cloud:**
- Production workloads
- Need best quality
- No good GPU
- High volume (cloud may be faster)

---

## Next Steps

1. ✅ **Test with sample workflow**
   ```bash
   # In UI at http://localhost:8501
   therapist departed T001
   ```

2. ✅ **Run full test suite**
   ```bash
   # In UI
   run tests
   ```

3. ✅ **Try different models**
   - Download Llama 3.1 8B
   - Compare quality vs GPT-OSS-20B
   - Find best speed/quality balance

4. ✅ **Set up hybrid mode**
   - Keep local for dev
   - Add cloud API for production
   - Use local as fallback

---

## Support

- **LM Studio Docs**: https://lmstudio.ai/docs
- **LiteLLM Docs**: https://docs.litellm.ai
- **This Project**: See `docs/LM_STUDIO_SETUP.md`

---

## ✅ Checklist

- [ ] LM Studio installed
- [ ] GPT-OSS-20B model downloaded
- [ ] Model loaded in LM Studio
- [ ] Server started on port 1234
- [ ] `.env` configured (`USE_LOCAL_MODEL=true`)
- [ ] Docker services started (`make docker-up`)
- [ ] Test script passed (`./test_lm_studio.sh`)
- [ ] UI working (http://localhost:8501)
- [ ] Test workflow completed successfully

---

🎉 **You're now running on 100% FREE local models!**

No API costs. No limits. Complete privacy. 🔒💰

