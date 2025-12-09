# ✅ DevOps Deployment Checklist

## Pre-Deployment (5 minutes)

- [ ] **Create GitHub repository**: `webpt-demo` at https://github.com/madhan-here-now/webpt-demo
- [ ] **Get Azure OpenAI credentials**:
  - [ ] AZURE_API_KEY
  - [ ] AZURE_API_BASE (e.g., https://your-instance.openai.azure.com/)
  - [ ] AZURE_DEPLOYMENT_NAME
- [ ] **Review** `deploy/env.template` and prepare actual `.env` file

## Deployment Steps (10 minutes)

### Option 1: Docker (Recommended)
- [ ] Build image: `docker build -t webpt-demo .`
- [ ] Create `.env` file with Azure credentials
- [ ] Run: `docker-compose -f deploy/docker-compose.production.yml up -d`
- [ ] Verify health: `curl http://localhost:8000/health`

### Option 2: Manual
- [ ] Install Python 3.11+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set environment variables from `.env` file
- [ ] Start API: `python api/server.py`
- [ ] (Optional) Start UI: `streamlit run demo/chat_ui.py`

## Verification (2 minutes)

- [ ] **API Health**: http://localhost:8000/health → Should return `{"status":"healthy"}`
- [ ] **Schedule UI**: http://localhost:8000/schedule.html → Should show provider calendar
- [ ] **Email Inbox**: http://localhost:8000/emails.html → Should show sent emails
- [ ] **API Docs**: http://localhost:8000/docs → Swagger UI should load

## Demo Endpoints

### Key URLs:
1. **Schedule Calendar**: http://localhost:8000/schedule.html
   - Shows provider availability
   - Can mark providers unavailable
   - Real-time appointment updates

2. **Email Inbox**: http://localhost:8000/emails.html
   - Shows AI-generated patient emails
   - Patient can accept/decline appointments

3. **API Documentation**: http://localhost:8000/docs
   - Interactive Swagger UI
   - Test all endpoints

### Quick API Tests:
```bash
# List appointments
curl http://localhost:8000/api/appointments

# List providers
curl http://localhost:8000/api/providers

# List patients
curl http://localhost:8000/api/patients
```

## Post-Deployment

- [ ] **Test provider unavailability workflow**:
  1. Go to http://localhost:8000/schedule.html
  2. Click "Mark Unavailable" on a provider
  3. Verify appointments are reassigned
  4. Check emails at http://localhost:8000/emails.html

- [ ] **Verify Azure LLM is working**:
  - Check logs for Azure API calls
  - Should NOT see "mock" or "local" LLM references
  - Reassignments should use real AI reasoning

## Troubleshooting

### Issue: "Connection refused"
```bash
# Check if port is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>
```

### Issue: "Azure API error"
```bash
# Verify environment variables
echo $AZURE_API_KEY
echo $AZURE_API_BASE

# Check .env file is loaded (Docker)
docker exec webpt-demo-api env | grep AZURE
```

### Issue: "No data showing"
```bash
# Check data files exist
ls -la data/*.json

# Verify volume mount (Docker)
docker exec webpt-demo-api ls -la /app/data/
```

## Production Checklist

- [ ] Set up reverse proxy (nginx/caddy) for HTTPS
- [ ] Configure firewall rules (only expose 80/443)
- [ ] Set up monitoring (health check endpoint)
- [ ] Configure log aggregation
- [ ] Set up automated backups for `/app/data/`
- [ ] Configure rate limiting on API endpoints
- [ ] Set up Langfuse for LLM observability (optional)

## Support Contact

If deployment fails or issues arise:
1. Check Docker logs: `docker logs webpt-demo-api`
2. Check application logs in `logs/` directory
3. Verify all environment variables are set correctly
4. Ensure Azure OpenAI endpoint is accessible from server

---

## ⏱️ Expected Timeline

- **Setup**: 5 minutes
- **Deployment**: 10 minutes
- **Verification**: 2 minutes
- **Total**: ~15-20 minutes

## 🎯 Success Criteria

✅ API returns healthy status
✅ Schedule UI loads and shows providers with "PT" suffix
✅ Can mark provider unavailable and see reassignments
✅ Emails are generated and visible in inbox
✅ Azure LLM is being used (check logs for confirmation)

