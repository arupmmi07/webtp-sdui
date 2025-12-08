# DevOps Quick Start - 10 Minute Deployment

## 🚀 What You Need (5 minutes to setup)

### 1. Environment Variables (.env file)
```bash
# Required for Azure LLM
AZURE_API_KEY=your-azure-openai-key
AZURE_API_BASE=https://your-instance.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview
AZURE_DEPLOYMENT_NAME=your-deployment-name

# Optional: Observability (Langfuse)
LANGFUSE_PUBLIC_KEY=pk-lf-xxx
LANGFUSE_SECRET_KEY=sk-lf-xxx
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 2. Ports to Expose
- **8000**: API Server (FastAPI)
- **8501**: UI Server (Streamlit) - Optional

### 3. Data Persistence
Mount volume: `/app/data` - Contains JSON databases

---

## 🐳 Docker Deployment (Recommended)

```bash
# 1. Build image
docker build -t webtp-demo .

# 2. Run with environment variables
docker run -d \
  --name webtp-demo \
  -p 8000:8000 \
  -p 8501:8501 \
  -e AZURE_API_KEY=your-key \
  -e AZURE_API_BASE=your-base-url \
  -e AZURE_DEPLOYMENT_NAME=your-deployment \
  -v $(pwd)/data:/app/data \
  webtp-demo

# 3. Check health
curl http://localhost:8000/health
```

---

## 📦 Manual Deployment (Without Docker)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export AZURE_API_KEY=your-key
export AZURE_API_BASE=your-base-url
export AZURE_DEPLOYMENT_NAME=your-deployment

# 3. Start API server
python api/server.py

# 4. (Optional) Start UI in another terminal
streamlit run demo/chat_ui.py
```

---

## 🔍 Health Checks

```bash
# API Health
curl http://localhost:8000/health

# Expected response:
{"status":"healthy","message":"Healthcare Operations Assistant API is running"}
```

---

## 📊 Key Endpoints for Demo

1. **Schedule UI**: http://localhost:8000/schedule.html
2. **Email Inbox**: http://localhost:8000/emails.html
3. **API Docs**: http://localhost:8000/docs
4. **Chat UI** (optional): http://localhost:8501

---

## ⚡ Quick Test

```bash
# Test appointment listing
curl http://localhost:8000/api/appointments

# Test provider listing
curl http://localhost:8000/api/providers
```

---

## 🚨 Common Issues

**Issue**: "Connection refused"
- **Fix**: Check if port 8000 is available: `lsof -i :8000`

**Issue**: "Azure API error"
- **Fix**: Verify AZURE_API_KEY and AZURE_API_BASE are set correctly

**Issue**: "No appointments showing"
- **Fix**: Check data volume is mounted: `ls data/appointments.json`

---

## 📞 Support

If deployment fails, check:
1. `docker logs webtp-demo` (if using Docker)
2. Environment variables are set
3. Ports 8000/8501 are not in use

