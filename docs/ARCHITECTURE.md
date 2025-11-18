# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│  CLI Interface (Demo)                               │
│  - Interactive command line                         │
│  - Real-time progress display                       │
│  - Audit log viewer                                 │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  LangFuse (Observability Platform)                  │
│  - Prompt versioning & management                   │
│  - Request tracing & debugging                      │
│  - Cost tracking & analytics                        │
│  - A/B testing & experimentation                    │
└──────────────────┬──────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  LiteLLM (LLM Gateway/Router)                       │
│  - Unified API for 100+ providers                   │
│  - Automatic fallbacks (Claude→GPT-4→Gemini)        │
│  - Load balancing & rate limiting                   │
│  - Cost optimization & caching                      │
└──────────────────┬──────────────────────────────────┘
                   ↓
         ┌─────────┴──────────┬──────────────┐
         ↓                    ↓              ↓
    [Anthropic]          [OpenAI]        [Google]
    Claude Sonnet        GPT-4           Gemini Pro
    (Primary)           (Fallback 1)    (Fallback 2)
         └─────────┬──────────┴──────────────┘
                   ↓
┌─────────────────────────────────────────────────────┐
│  LangGraph Orchestrator                             │
│  - Reads PDF knowledge for ALL rules                │
│  - Orchestrates 6-stage workflow                    │
│  - Emits events for A2A communication               │
│  - Makes dynamic decisions                          │
└──────────────────┬──────────────────────────────────┘
                   ↓
         ┌─────────────────┐
         │  Event Queue    │
         │  (Python Queue  │
         │   → Redis later)│
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┐
    ↓                           ↓
┌───────────────────────────────────────────────┐
│  SMART SCHEDULING AGENT                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Trigger  │  │ Matching │  │ Backfill │   │
│  │ Handler  │  │ & Scoring│  │ & Audit  │   │
│  └──────────┘  └──────────┘  └──────────┘   │
│  • Priority Scoring  • 8 Filters             │
│  • No-Show Risk     • 5 Scoring Factors      │
│  • Waitlist Mgmt    • Compliance Gating      │
└───────────────────────────────────────────────┘
                    ↓
┌───────────────────────────────────────────────┐
│  PATIENT ENGAGEMENT AGENT                     │
│  ┌──────────────────────────────────────┐    │
│  │ Automated Patient Offer Flow         │    │
│  └──────────────────────────────────────┘    │
│  • Multi-Channel (SMS/Email/IVR)             │
│  • Consent Management                        │
│  • Response Handling                         │
└───────────────────────────────────────────────┘
                   ↓
     ┌─────────────────────────────────┐
     │  MCP Servers (2)                │
     ├─────────────────┬───────────────┤
     │ Knowledge MCP   │ Domain API MCP│
     │ - Matching      │ - Provider API│
     │   rules         │ - Patient API │
     │ - Scoring       │ - Appointment │
     │   weights       │ - Notification│
     │ - Payer rules   │ - Waitlist API│
     │ - POC policies  │               │
     │ - Workflow      │               │
     └─────────────────┴───────────────┘
```

## Layered Architecture

### Layer 0: Observability & Gateway (Production Infrastructure)

**Purpose:** Observability, monitoring, and vendor abstraction at the infrastructure level

```
LangFuse (Observability Platform)
├── Prompt Management       # Version and manage prompts in UI
├── Tracing                # Trace every LLM call end-to-end
├── Analytics              # Cost, latency, error tracking
└── A/B Testing            # Test prompt variations

LiteLLM (LLM Gateway)
├── Unified API            # One API for 100+ providers
├── Automatic Fallbacks    # Claude → GPT-4 → Gemini
├── Load Balancing         # Distribute across instances
├── Rate Limiting          # Prevent quota exhaustion
└── Cost Optimization      # Caching, routing
```

### Layer 1: Interfaces (Vendor-Agnostic)

**Purpose:** Abstract all external dependencies to enable plug-and-play

```
interfaces/
├── llm_provider.py         # Abstract LLM interface
├── workflow_engine.py      # Abstract workflow orchestrator
├── event_bus.py           # Abstract event system
└── risk_calculator.py     # Abstract no-show risk calculation
```

**Key Principle:** Code to interfaces, not implementations

### Layer 2: Adapters (Pluggable Implementations)

**Purpose:** Concrete implementations that can be swapped

```
adapters/
├── llm/
│   ├── litellm_adapter.py      # LiteLLM (PRODUCTION - unified gateway)
│   │                           # Handles: Claude, GPT-4, Gemini, Ollama, etc.
│   └── [future custom adapters if needed]
├── workflow/
│   ├── langgraph_adapter.py    # LangGraph (recommended)
│   └── custom_adapter.py       # Simple Python (fallback)
└── events/
    ├── memory_queue.py         # In-memory (start with this)
    └── redis_adapter.py        # Redis (scale later)
```

**Swap Example:**
```python
# Swap LLM provider by changing config - ZERO code changes!
# config/litellm_config.yaml
default_model: claude-sonnet      # ← Change to gpt-4-fallback or gemini-fallback

# Or swap entire adapter
from adapters.llm import LiteLLMAdapter
llm = LiteLLMAdapter(model="claude-sonnet")  # Handles all providers!
```

### Layer 3: Domain Logic (Business Rules)

**Purpose:** Core business logic independent of infrastructure

```
agents/
├── smart_scheduling_agent.py      # SMART SCHEDULING AGENT
│   ├── trigger_handler()          # Step 1: Identify affected appointments
│   ├── filter_candidates()        # Step 2: Match candidate filtering
│   ├── score_and_gate()          # Step 3: Compliance & score gating
│   ├── backfill_automation()     # Step 5: Waitlist & backfill
│   └── reconciliation()          # Step 6: Final reconciliation
│
└── patient_engagement_agent.py    # PATIENT ENGAGEMENT AGENT
    └── automated_offer_flow()     # Step 4: Patient consent flow
```

### Layer 4: Infrastructure (External Systems)

**Purpose:** Integration with external services via MCP

```
mcp_servers/
├── knowledge/
│   ├── server.py          # Expose knowledge docs
│   └── pdf_parser.py      # Parse PDF files
└── domain_api/
    ├── server.py          # Combined API server
    ├── provider_api.py    # Provider CRUD
    ├── patient_api.py     # Patient CRUD
    ├── appointment_api.py # Appointment CRUD
    ├── notification_api.py# SMS/Email/IVR
    └── waitlist_api.py    # Waitlist management
```

## Data Flow

### 6-Stage Workflow

```
Stage 1: TRIGGER (Smart Scheduling Agent)
Input: Therapist unavailability event
Process: Calculate priority scores for all affected appointments
Output: Prioritized appointment list
Event: trigger_detected
Agent: Smart Scheduling Agent

Stage 2: FILTERING (Smart Scheduling Agent)
Input: Appointment + Available providers
Process: Apply 8 hard constraint filters
Output: Qualified provider list (3-5 providers)
Event: candidates_filtered
Agent: Smart Scheduling Agent

Stage 3: SCORING & GATING (Smart Scheduling Agent)
Input: Qualified providers + Patient profile
Process: Apply 5 scoring factors + compliance gating
Output: Ranked provider list (top 3)
Event: candidates_scored
Agent: Smart Scheduling Agent

Stage 4: CONSENT (Patient Engagement Agent)
Input: Top-ranked provider + Patient preferences
Process: Send offer via preferred channel, wait for response
Output: Booked appointment OR declined
Event: appointment_booked OR consent_declined_all
Agent: Patient Engagement Agent

Stage 5: BACKFILL (Smart Scheduling Agent)
Input: Freed slot + High-risk patient list + Original patient availability
Process: Fill freed slot + Reschedule original patient
Output: Both slots filled OR HOD assignment
Event: backfill_completed OR manual_review_needed
Agent: Smart Scheduling Agent

Stage 6: AUDIT (Smart Scheduling Agent)
Input: All events from workflow
Process: Aggregate, log, report, reconcile
Output: Complete audit trail + Reports
Event: session_complete
Agent: Smart Scheduling Agent
```

## Agent-to-Agent (A2A) Communication

### Event-Driven Pattern

```python
# Agent 1 emits event
event_bus.emit("candidates_scored", {
    "appointment_id": "A001",
    "candidates": [...]
})

# Agent 2 listens and responds
@event_bus.subscribe("candidates_scored")
def handle_scored_candidates(event):
    # Process and emit next event
    result = consent_agent.execute(event)
    event_bus.emit("appointment_booked", result)
```

**Benefits:**
- Loose coupling between agents
- Easy to add new agents
- Handles concurrency naturally
- Audit trail built-in

## MCP Integration

### Knowledge MCP Server

**Exposes:** Knowledge documents as resources

```
Resources:
- knowledge://matching-rules
- knowledge://scoring-weights
- knowledge://payer-rules
- knowledge://poc-policies
- knowledge://workflow-steps

Tools:
- search_knowledge(query: str) → results
```

### Domain API MCP Server

**Exposes:** All business APIs as tools

```
Tools (Provider):
- get_provider(provider_id) → Provider
- list_providers(filters) → List[Provider]
- check_availability(provider_id, date) → bool

Tools (Patient):
- get_patient(patient_id) → Patient
- get_preferences(patient_id) → Preferences
- get_no_show_risk(patient_id) → float

Tools (Appointment):
- get_appointment(appointment_id) → Appointment
- update_appointment(appointment_id, updates) → Appointment
- create_appointment(data) → Appointment

Tools (Notification):
- send_sms(phone, message) → MessageID
- send_email(email, subject, body) → MessageID
- send_ivr(phone, script) → CallID

Tools (Waitlist):
- add_to_waitlist(slot) → WaitlistEntry
- query_waitlist(criteria) → List[WaitlistEntry]
- fill_slot(slot_id, patient_id) → Appointment
```

## Configuration System

### Multi-Level Configuration

```yaml
# config/llm_config.yaml
provider: anthropic  # Swap here to change LLM
anthropic:
  model: claude-sonnet-4-20250514
  api_key: ${ANTHROPIC_API_KEY}

# config/mcp_servers.yaml
knowledge:
  type: stdio
  command: python
  args: ["-m", "mcp_servers.knowledge.server"]

domain_api:
  type: stdio
  command: python
  args: ["-m", "mcp_servers.domain_api.server"]
  env:
    BACKEND: mock  # Swap to 'webpt' for real API

# config/scoring_weights.yaml
continuity: 40
specialty: 35
preference: 30
load_balance: 25
day_match: 20

# config/payer_rules.yaml
medicare:
  requires_poc: true
  requires_prior_auth: false
  approved_providers_only: true
ppo:
  requires_poc: false
  requires_prior_auth: false
workers_comp:
  requires_poc: true
  requires_prior_auth: true
  requires_employer_auth: true
```

## Scalability Considerations

### Current (MVP):
- In-memory event queue
- Mock APIs
- Single process
- Handles: 15-50 appointments concurrently

### Phase 2 (Production):
- Redis event queue
- Real API connections
- Multi-process
- Handles: 100s of appointments concurrently

### Phase 3 (Enterprise):
- Distributed event bus (Kafka/RabbitMQ)
- Microservices (each agent = service)
- Kubernetes deployment
- Handles: 1000s of appointments concurrently

## Security & Compliance

### HIPAA Compliance

- **PHI Protection:** All patient data encrypted in transit and at rest
- **Audit Logging:** Complete audit trail of all data access
- **Access Control:** Role-based access to sensitive data
- **Data Retention:** 7-year retention per HIPAA requirements

### Authentication & Authorization

```
Future Implementation:
- OAuth2 for API authentication
- JWT tokens for session management
- Role-based access control (RBAC)
- API key rotation policies
```

## Extension Points

### Adding a New Agent

1. Create agent class inheriting from base
2. Implement `execute()` method
3. Subscribe to relevant events
4. Emit events for downstream agents
5. Update workflow graph to include new node

### Adding a New LLM Provider

1. Create adapter in `adapters/llm/`
2. Implement `LLMProvider` interface
3. Update `config/llm_config.yaml`
4. Change one line: `provider: new_provider`

### Adding a New API Backend

1. Create backend module in `mcp_servers/domain_api/`
2. Implement same interface as mock
3. Update `config/mcp_servers.yaml`
4. Change one line: `BACKEND: new_backend`

### Adding a New Workflow

1. Create new knowledge documents
2. Define workflow stages in markdown
3. LLM reads and executes dynamically
4. No code changes required!

## Technology Stack

### Production Infrastructure:
- **LLM Gateway:** LiteLLM (unified API for 100+ providers)
- **Observability:** LangFuse (tracing, prompts, analytics)
- **Primary LLM:** Anthropic Claude Sonnet 4
- **Fallback LLMs:** OpenAI GPT-4, Google Gemini Pro
- **Local Dev:** Ollama (free, no API key)

### Core:
- **Language:** Python 3.11+
- **Workflow:** LangGraph
- **MCP:** Anthropic MCP SDK

### Libraries:
- `litellm` - LLM gateway/router
- `langfuse` - Observability & prompt management
- `langgraph` - Workflow orchestration
- `mcp` - MCP server/client
- `pydantic` - Data validation
- `pyyaml` - Configuration
- `pypdf2` - PDF parsing

### Development:
- `pytest` - Testing
- `black` - Code formatting
- `mypy` - Type checking

## Performance Targets

| Metric | MVP Target | Production Target |
|--------|-----------|------------------|
| Trigger Detection | <30 sec | <10 sec |
| Filtering + Scoring | <15 sec per appointment | <5 sec |
| Consent Wait | 24 hours (timeout) | 24 hours |
| Backfill | <6 hours | <2 hours |
| Total Resolution | <8 hours average | <4 hours average |
| Concurrent Appointments | 15-50 | 500+ |
| System Uptime | 95% | 99.5% |

## Monitoring & Observability

### Metrics to Track

- **Performance:** Agent execution times, API response times
- **Business:** Success rates, revenue preserved, patient satisfaction
- **System:** CPU/Memory usage, event queue depth, error rates
- **Compliance:** POC validation rate, payer rule violations

### Logging Levels

- **DEBUG:** Detailed execution traces
- **INFO:** Key business events
- **WARNING:** Recoverable issues
- **ERROR:** System failures
- **AUDIT:** All patient data access

## Deployment Architecture

### MVP (Local):
```
Single Machine
├── Python Process
│   ├── Orchestrator
│   ├── Agents
│   └── Event Queue (in-memory)
├── MCP Server 1 (Knowledge)
└── MCP Server 2 (Domain API)
```

### Production (Cloud):
```
Kubernetes Cluster
├── Pod: Orchestrator (LangGraph)
├── Pod: Agent Pool (3 replicas)
├── Pod: Knowledge MCP Server
├── Pod: Domain API MCP Server
├── Service: Redis (Event Bus)
└── Service: PostgreSQL (Audit Logs)
```

