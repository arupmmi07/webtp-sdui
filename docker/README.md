# Docker Deployment Guide

This directory contains Docker configuration for running the Healthcare Operations Assistant with LiteLLM integration.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Network                          │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐    ┌─────────────┐ │
│  │   Streamlit  │─────▶│  API Server  │───▶│  LiteLLM    │ │
│  │   UI :8501   │      │   :8000      │    │  Proxy      │ │
│  └──────────────┘      └──────────────┘    │   :4000     │ │
│                                              └──────┬──────┘ │
│                                                     │        │
│                                              ┌──────▼──────┐ │
│                                              │  PostgreSQL │ │
│                                              │   (logs)    │ │
│                                              └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Setup Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

### 2. Run with Mock LLM (Demo Mode)

```bash
# No API keys needed - uses mocked responses
docker-compose up -d

# Access the UI
open http://localhost:8501

# View logs
docker-compose logs -f
```

### 3. Run with Real LLM (Production Mode)

```bash
# Edit .env and set:
# - USE_MOCK_LLM=false
# - ANTHROPIC_API_KEY=your-real-key

# Start services
docker-compose up -d

# Monitor LiteLLM logs
docker-compose logs -f litellm
```

## Services

### LiteLLM Proxy (`:4000`)
- Unified gateway for all LLM providers
- Handles fallbacks, retries, rate limiting
- Logs to PostgreSQL for observability
- **Swagger UI**: http://localhost:4000/

### API Server (`:8000`)
- Flask REST API
- Provides data endpoints for UI
- Handles patient response simulation
- **Health Check**: http://localhost:8000/health

### Streamlit UI (`:8501`)
- Interactive chat interface
- Workflow visualization
- EMR records viewer
- **URL**: http://localhost:8501/

### PostgreSQL
- Stores LiteLLM logs and cache
- Internal service (not exposed)

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USE_MOCK_LLM` | Use mock vs real LLM | `true` |
| `ANTHROPIC_API_KEY` | Anthropic API key | Required for real LLM |
| `LITELLM_MASTER_KEY` | LiteLLM proxy auth | `sk-1234` |
| `LANGFUSE_PUBLIC_KEY` | LangFuse observability | Optional |
| `LANGFUSE_SECRET_KEY` | LangFuse observability | Optional |

### LiteLLM Configuration

Edit `config/litellm_config.yaml` to:
- Add/remove LLM providers
- Configure fallback strategies
- Set rate limits and budgets
- Enable/disable caching

## Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Rebuild after code changes
docker-compose up -d --build

# Clean everything (including volumes)
docker-compose down -v
```

## Switching from Mock to Real LLM

### Step 1: Update Environment
```bash
# Edit .env
USE_MOCK_LLM=false
ANTHROPIC_API_KEY=sk-ant-api03-...
```

### Step 2: Restart Services
```bash
docker-compose restart api ui
```

### Step 3: Verify
```bash
# Check LiteLLM is receiving requests
docker-compose logs -f litellm

# Test in UI
# Type: "therapist departed T001"
# You should see real LLM calls in logs
```

## Troubleshooting

### Issue: Port already in use
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9
lsof -ti:8501 | xargs kill -9
lsof -ti:4000 | xargs kill -9
```

### Issue: LiteLLM API key error
```bash
# Verify API key is set
docker-compose exec litellm env | grep ANTHROPIC

# Check LiteLLM logs
docker-compose logs litellm
```

### Issue: Services can't communicate
```bash
# Check network
docker network inspect schedule_healthcare-network

# Restart network
docker-compose down
docker-compose up -d
```

### Issue: Database connection error
```bash
# Wait for PostgreSQL to be ready
docker-compose logs litellm-db

# Reset database
docker-compose down -v
docker-compose up -d
```

## Monitoring

### LiteLLM Dashboard
```bash
# Access Swagger UI
open http://localhost:4000/

# View logs
docker-compose logs -f litellm
```

### Health Checks
```bash
# Check all services
curl http://localhost:8000/health
curl http://localhost:4000/health

# Via docker
docker-compose ps
```

## Cost Management

LiteLLM proxy provides built-in cost tracking:

1. **Budget Limits**: Set per-model daily budgets in `config/litellm_config.yaml`
2. **Rate Limiting**: Configure request limits per model
3. **Caching**: Enable Redis cache to reduce duplicate calls
4. **Fallbacks**: Use cheaper models as fallbacks (e.g., Haiku → GPT-4o-mini)

### View Costs
```bash
# Check LiteLLM logs for cost tracking
docker-compose logs litellm | grep -i "cost\|budget"
```

## Production Deployment

For production, consider:

1. **Use proper secrets management** (AWS Secrets Manager, Azure Key Vault)
2. **Enable SSL/TLS** (nginx reverse proxy)
3. **Add authentication** (OAuth, API keys)
4. **Scale with Docker Swarm or Kubernetes**
5. **Use managed PostgreSQL** (AWS RDS, Azure Database)
6. **Set up monitoring** (Prometheus, Grafana)
7. **Configure backups** (PostgreSQL dumps)

## Additional Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Streamlit in Docker](https://docs.streamlit.io/knowledge-base/tutorials/deploy/docker)

