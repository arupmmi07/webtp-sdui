# AWS AgentCore Flow Diagram
## Visual Architecture for Appointment Rescheduling Workflow

---

## High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRIGGER LAYER                                      │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   EHR System │  │   Calendar   │  │ Admin Portal │  │ Patient API  │  │
│  │  (WebPT/     │  │ Integration  │  │  (Manual)    │  │ (Mobile App) │  │
│  │   Athena)    │  │              │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                         │
│                                    ↓                                         │
│                    ┌───────────────────────────────┐                        │
│                    │   AWS API Gateway             │                        │
│                    │   POST /api/workflow/trigger  │                        │
│                    │   • Authentication            │                        │
│                    │   • Rate Limiting             │                        │
│                    │   • Request Validation        │                        │
│                    └───────────────┬───────────────┘                        │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│              AMAZON BEDROCK AGENTCORE RUNTIME                                │
│              (Fully-Managed, Serverless, Auto-Scaling)                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │              SUPERVISOR ORCHESTRATOR AGENT                           │   │
│  │              (Long-Running Session, Up to 8 Hours)                  │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │  Prompt Management (LangFuse)                                │   │   │
│  │  │  • Versioned prompts                                         │   │   │
│  │  │  • A/B testing labels (production/experiment-v1)             │   │   │
│  │  │  • Cost tracking per version                                  │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │  AgentCore Memory                                             │   │   │
│  │  │  • Short-term: Session state                                  │   │   │
│  │  │  • Long-term: Patient preferences, provider history           │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  │  Workflow Orchestration (6 Stages):                                 │   │
│  │                                                                      │   │
│  │  Stage 1: Trigger Detection ────────────────────────────────────┐   │   │
│  │  Stage 2: Candidate Filtering ────────────────────────────────┐ │   │   │
│  │  Stage 3: Scoring & Ranking ─────────────────────────────────┐ │ │   │   │
│  │  Stage 4: Quality Assurance ──────────────────────────────┐ │ │ │   │   │
│  │  Stage 5: Patient Consent ───────────────────────────────┐ │ │ │ │   │   │
│  │  Stage 6: Booking & Backfill ──────────────────────────┐ │ │ │ │ │   │   │
│  │  Stage 7: Audit & Reporting ───────────────────────────┐ │ │ │ │ │ │   │   │
│  │                                                         │ │ │ │ │ │ │   │   │
│  │  ┌──────────────────────────────────────────────────┐ │ │ │ │ │ │ │   │   │
│  │  │  Specialized Agents (Sub-Agents)                  │ │ │ │ │ │ │   │   │
│  │  │                                                    │ │ │ │ │ │ │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────┐ │ │ │ │ │ │ │   │   │
│  │  │  │   Smart      │  │   Patient   │  │ Backfill │ │ │ │ │ │ │   │   │
│  │  │  │  Scheduling  │  │ Engagement  │  │  Agent   │ │ │ │ │ │ │   │   │
│  │  │  │   Agent      │  │   Agent     │  │          │ │ │ │ │ │ │   │   │
│  │  │  └──────────────┘  └──────────────┘  └──────────┘ │ │ │ │ │ │ │   │   │
│  │  │                                                    │ │ │ │ │ │ │   │   │
│  │  │  ┌──────────────┐  ┌──────────────┐              │ │ │ │ │ │ │   │   │
│  │  │  │   Quality    │  │    Audit     │              │ │ │ │ │ │ │   │   │
│  │  │  │  Assurance   │  │    Agent    │              │ │ │ │ │ │ │   │   │
│  │  │  │   Agent      │  │              │              │ │ │ │ │ │ │   │   │
│  │  │  └──────────────┘  └──────────────┘              │ │ │ │ │ │ │   │   │
│  │  └──────────────────────────────────────────────────┘ │ │ │ │ │ │ │   │   │
│  └────────────────────────────────────────────────────────┘ │ │ │ │ │ │   │   │
│                                                             │ │ │ │ │ │   │   │
│  ┌─────────────────────────────────────────────────────────┘ │ │ │ │ │   │   │
│  │  Agent-to-Agent Communication (Built-in)                  │ │ │ │ │   │   │
│  └────────────────────────────────────────────────────────────┘ │ │ │ │   │   │
│                                                                  │ │ │ │   │   │
│  ┌──────────────────────────────────────────────────────────────┘ │ │ │   │   │
│  │  AGENTCORE GATEWAY (MCP Integration)                            │ │ │   │   │
│  │  • Transforms REST APIs → MCP Tools                            │ │ │   │   │
│  │  • Semantic tool discovery                                      │ │ │   │   │
│  │  • Authentication & authorization                               │ │ │   │   │
│  │  • Rate limiting & throttling                                   │ │ │   │   │
│  └──────────────────────────────────────────────────────────────────┘ │ │   │   │
└────────────────────────────────────────────────────────────────────────┘ │ │   │   │
                                                                            │ │ │   │   │
                                                                            ↓ ↓ ↓   ↓   ↓
┌─────────────────────────────────────────────────────────────────────────────┐ │ │   │   │
│                    EXISTING BACKEND SYSTEMS                                  │ │ │   │   │
│                    (Connected via AgentCore Gateway)                         │ │ │   │   │
│                                                                             │ │ │   │   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │ │   │   │
│  │   Provider   │  │   Patient    │  │ Appointment  │  │ Notification │  │ │ │   │   │
│  │   Management │  │  Management  │  │  Scheduling  │  │   Services   │  │ │ │   │   │
│  │     API      │  │     API      │  │     API      │  │ (SMS/Email)   │  │ │ │   │   │
│  │              │  │              │  │              │  │              │  │ │ │   │   │
│  │  • get_      │  │  • get_      │  │  • get_      │  │  • send_email │  │ │ │   │   │
│  │    provider  │  │    patient  │  │    appointment│  │  • send_sms   │  │ │ │   │   │
│  │  • list_     │  │  • get_     │  │  • update_   │  │  • send_ivr   │  │ │ │   │   │
│  │    providers │  │    preferences│ │    appointment│  │              │  │ │ │   │   │
│  │  • check_    │  │  • update_  │  │  • create_   │  │              │  │ │ │   │   │
│  │    availability│ │    patient  │  │    appointment│  │              │  │ │ │   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │ │ │   │   │
│                                                                             │ │ │   │   │
│  ┌──────────────┐  ┌──────────────┐                                      │ │ │   │   │
│  │   Waitlist   │  │   Knowledge   │                                      │ │ │   │   │
│  │  Management │  │     Base      │                                      │ │ │   │   │
│  │     API     │  │ (Compliance/  │                                      │ │ │   │   │
│  │             │  │  Payer Rules) │                                      │ │ │   │   │
│  │  • add_to_  │  │               │                                      │ │ │   │   │
│  │    waitlist │  │  • search_    │                                      │ │ │   │   │
│  │  • query_   │  │    compliance │                                      │ │ │   │   │
│  │    waitlist │  │  • get_payer_ │                                      │ │ │   │   │
│  │  • fill_slot│  │    rules      │                                      │ │ │   │   │
│  └──────────────┘  └──────────────┘                                      │ │ │   │   │
└─────────────────────────────────────────────────────────────────────────────┘ │ │   │   │
                                                                                │ │   │   │
                                                                                ↓ ↓   ↓   ↓
┌─────────────────────────────────────────────────────────────────────────────┐ │ │   │   │
│                    OBSERVABILITY & MONITORING                               │ │ │   │   │
│                                                                             │ │ │   │   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │ │ │   │   │
│  │ AgentCore        │  │ LangFuse         │  │ Custom           │        │ │ │   │   │
│  │ Observability   │  │ (Prompts &       │  │ Dashboards       │        │ │ │   │   │
│  │ (CloudWatch)     │  │  Analytics)     │  │ (Business        │        │ │ │   │   │
│  │                  │  │                  │  │  Metrics)        │        │ │ │   │   │
│  │ • Token usage    │  │ • Prompt         │  │ • Appointments   │        │ │ │   │   │
│  │ • Latency        │  │   versioning     │  │   processed      │        │ │ │   │   │
│  │ • Error rates    │  │ • A/B testing    │  │ • Success rate   │        │ │ │   │   │
│  │ • Session replay │  │ • Cost tracking  │  │ • Compliance     │        │ │ │   │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘        │ │ │   │   │
└─────────────────────────────────────────────────────────────────────────────┘ │ │   │   │
                                                                                │ │   │   │
                                                                                └─┴───┴───┘
                                                                                  │
                                                                                  ↓
                                                                    [Workflow Complete]
                                                                    [Audit Log Generated]
```

---

## Detailed Workflow Execution Flow

### Stage-by-Stage Breakdown

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW EXECUTION DETAIL                                │
└─────────────────────────────────────────────────────────────────────────────┘

[TRIGGER EVENT]
    │
    │ Provider Unavailable Event
    │ {provider_id: "T001", reason: "departure", start_date: "2025-02-01"}
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: TRIGGER DETECTION                                                  │
│ Agent: Smart Scheduling Agent                                               │
│ Tools: Provider API, Appointment API                                       │
│                                                                             │
│ Input:  provider_id="T001"                                                  │
│ Process:                                                                   │
│   1. Get provider details (Provider API)                                    │
│   2. Find all affected appointments (Appointment API)                      │
│   3. Calculate priority scores                                              │
│ Output: {affected_appointments: [...], count: 15}                          │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: CANDIDATE FILTERING                                                │
│ Agent: Smart Scheduling Agent                                               │
│ Tools: Knowledge API (compliance rules), Provider API                       │
│                                                                             │
│ Input:  appointment + all_providers                                          │
│ Process:                                                                   │
│   1. Load compliance rules (Knowledge API)                                   │
│   2. Apply 8 hard filters:                                                 │
│      - Specialty match                                                      │
│      - Location constraints                                                │
│      - Availability                                                          │
│      - Payer rules                                                          │
│      - POC requirements                                                      │
│      - License status                                                       │
│      - Capacity limits                                                      │
│      - Geographic restrictions                                              │
│ Output: {qualified_providers: ["P001", "P004", "P003"], count: 3}           │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: SCORING & RANKING                                                  │
│ Agent: Smart Scheduling Agent                                               │
│ LLM: Claude Sonnet 4 (via Bedrock)                                          │
│ Tools: Knowledge API (scoring weights), Patient API                         │
│                                                                             │
│ Input:  qualified_providers + patient_profile                              │
│ Process:                                                                   │
│   1. Load scoring weights (Knowledge API)                                   │
│   2. LLM calculates scores using 6 factors:                                │
│      - Continuity (40 pts): Prior provider relationship                    │
│      - Specialty match (35 pts): Condition specialty match                 │
│      - Patient preference (30 pts): Gender, location, etc.                 │
│      - Load balance (25 pts): Provider capacity utilization                │
│      - Experience match (20 pts): Years of experience                      │
│      - Day/time match (10 pts): Preferred days/times                        │
│   3. Rank providers by total score                                          │
│ Output: {ranked_providers: [                                                │
│            {provider_id: "P001", score: 145, rank: 1},                     │
│            {provider_id: "P004", score: 120, rank: 2},                     │
│            {provider_id: "P003", score: 95, rank: 3}                       │
│         ]}                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: QUALITY ASSURANCE                                                  │
│ Agent: Quality Assurance Agent                                              │
│ Tools: Knowledge API (guardrails), Risk Calculator                          │
│                                                                             │
│ Input:  top-ranked assignments                                              │
│ Process:                                                                   │
│   1. Compliance validation:                                                 │
│      - POC requirements met?                                                │
│      - Payer rules satisfied?                                              │
│      - Distance constraints valid?                                         │
│   2. Data quality checks:                                                   │
│      - Provider availability confirmed?                                    │
│      - Patient eligibility verified?                                       │
│   3. Risk assessment:                                                       │
│      - No-show risk acceptable?                                             │
│      - Continuity score above threshold?                                    │
│ Output: {approved: [assignment_1, assignment_2],                           │
│          rejected: [assignment_3 (reason: "distance exceeds limit")]}        │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 5: PATIENT CONSENT                                                    │
│ Agent: Patient Engagement Agent                                             │
│ Tools: Notification API (email/SMS), Patient API                            │
│                                                                             │
│ Input:  approved assignments                                                │
│ Process:                                                                   │
│   1. Get patient communication preferences (Patient API)                   │
│   2. Generate personalized message (LLM + templates)                        │
│   3. Send offer via preferred channel:                                      │
│      - Email (with accept/decline links)                                   │
│      - SMS (with response instructions)                                     │
│      - IVR (automated phone call)                                           │
│   4. Wait for patient response (24-hour timeout)                          │
│ Output: {responses: [                                                       │
│            {appointment_id: "A001", response: "accepted", provider: "P001"},│
│            {appointment_id: "A002", response: "declined", provider: "P004"} │
│         ]}                                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 6: BOOKING & BACKFILL                                                 │
│ Agents: Smart Scheduling Agent + Backfill Agent                             │
│ Tools: Appointment API, Waitlist API                                         │
│                                                                             │
│ Process:                                                                    │
│   For ACCEPTED assignments:                                                 │
│     1. Book appointment (Appointment API)                                    │
│     2. Send confirmation (Notification API)                                 │
│                                                                             │
│   For DECLINED appointments:                                                │
│     1. Add patient to waitlist (Waitlist API)                             │
│     2. Free up slot (Appointment API)                                      │
│     3. Find next patient from waitlist (Waitlist API)                      │
│     4. Attempt backfill (Backfill Agent)                                    │
│                                                                             │
│ Output: {booked: [appointment_1, appointment_2],                           │
│          backfilled: [appointment_3 → patient_5],                         │
│          waitlisted: [appointment_4]}                                       │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 7: AUDIT & REPORTING                                                   │
│ Agent: Audit Agent                                                          │
│ Tools: Audit API, Reporting API                                             │
│                                                                             │
│ Process:                                                                    │
│   1. Aggregate all workflow events                                          │
│   2. Generate compliance report                                             │
│   3. Create audit log (HIPAA-compliant)                                    │
│   4. Send summary report to administrators                                  │
│                                                                             │
│ Output: {audit_log: {...},                                                 │
│          compliance_report: {...},                                          │
│          summary: {                                                         │
│            appointments_processed: 15,                                       │
│            successfully_reassigned: 12,                                      │
│            waitlisted: 2,                                                    │
│            escalated_to_hod: 1                                              │
│          }}                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
[WORKFLOW COMPLETE]
```

---

## Prompt Management Flow (LangFuse)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PROMPT MANAGEMENT (LANGFUSE)                            │
└─────────────────────────────────────────────────────────────────────────────┘

[LangFuse Dashboard]
    │
    │ Prompt: "supervisor_orchestrator"
    │
    ├─ Version 1.0 (production)
    │  └─ Label: "production" (80% traffic)
    │
    ├─ Version 2.0 (experiment)
    │  └─ Label: "experiment-v1" (20% traffic)
    │
    └─ Version 2.1 (staging)
       └─ Label: "staging" (0% traffic, testing)

    │
    ↓
[AgentCore Runtime]
    │
    │ Load prompt with label:
    │
    ├─ Production workflows → "production" label
    │  └─ Uses Version 1.0
    │
    └─ Experiment workflows → "experiment-v1" label
       └─ Uses Version 2.0

    │
    ↓
[Metrics Collection]
    │
    ├─ Token usage per version
    ├─ Latency per version
    ├─ Success rate per version
    └─ Cost per version

    │
    ↓
[A/B Test Analysis]
    │
    └─ Compare experiment-v1 vs production
       └─ If experiment performs better:
          → Promote to production
          → Update traffic split
```

---

## A/B Testing Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         A/B TESTING FLOW                                    │
└─────────────────────────────────────────────────────────────────────────────┘

[Workflow Trigger]
    │
    ↓
[Traffic Split Logic]
    │
    ├─ workflow_id % 2 == 0
    │  └─ → Use "experiment-v1" prompt (50%)
    │
    └─ workflow_id % 2 == 1
       └─ → Use "production" prompt (50%)

    │
    ↓
[Execute Workflow]
    │
    ├─ Experiment Group (experiment-v1)
    │  └─ Metrics tracked with label: "experiment-v1"
    │
    └─ Control Group (production)
       └─ Metrics tracked with label: "production"

    │
    ↓
[Metrics Comparison]
    │
    ├─ Success Rate:
    │  ├─ experiment-v1: 92%
    │  └─ production: 88%
    │
    ├─ Average Latency:
    │  ├─ experiment-v1: 2.3 min
    │  └─ production: 2.8 min
    │
    └─ Cost per Appointment:
       ├─ experiment-v1: $0.15
       └─ production: $0.18

    │
    ↓
[Decision]
    │
    └─ experiment-v1 performs better:
       → Promote to production
       → Update traffic split: experiment-v1 = 100%
       → Create new experiment: experiment-v2
```

---

## Quality Assurance & Guardrails Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              QUALITY ASSURANCE & GUARDRAILS                                │
└─────────────────────────────────────────────────────────────────────────────┘

[Agent Output]
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ GUARDRAIL 1: Schema Validation                                             │
│ • Validate JSON structure                                                   │
│ • Check required fields                                                     │
│ • Type checking                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ├─ [FAIL] → Reject, return error to agent
    │
    └─ [PASS] ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ GUARDRAIL 2: Compliance Checks                                              │
│ • POC requirements met?                                                     │
│ • Payer rules satisfied?                                                    │
│ • HIPAA compliance verified?                                                │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ├─ [FAIL] → Reject, escalate to HOD
    │
    └─ [PASS] ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ GUARDRAIL 3: Business Rules                                                 │
│ • Distance constraints valid?                                                │
│ • Provider availability confirmed?                                          │
│ • Patient eligibility verified?                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ├─ [FAIL] → Reject, try next provider
    │
    └─ [PASS] ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ GUARDRAIL 4: Risk Assessment                                                │
│ • No-show risk acceptable?                                                   │
│ • Continuity score above threshold?                                          │
│ • Match quality sufficient?                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ├─ [FAIL] → Flag for review, proceed with warning
    │
    └─ [PASS] ↓
[APPROVED] → Proceed to next stage
```

---

## Observability & Monitoring Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              OBSERVABILITY & MONITORING                                     │
└─────────────────────────────────────────────────────────────────────────────┘

[Workflow Execution]
    │
    ├─ AgentCore Observability (CloudWatch)
    │  ├─ Token usage
    │  ├─ Latency (P50, P95, P99)
    │  ├─ Error rates
    │  ├─ Session duration
    │  └─ Session replay
    │
    ├─ LangFuse Analytics
    │  ├─ Prompt version performance
    │  ├─ Cost per prompt version
    │  ├─ A/B test results
    │  └─ Token usage breakdown
    │
    └─ Custom Dashboards
       ├─ Business metrics
       │  ├─ Appointments processed
       │  ├─ Success rate
       │  ├─ Patient satisfaction
       │  └─ Time to resolution
       │
       └─ Compliance metrics
          ├─ POC validation rate
          ├─ Payer rule violations
          └─ Audit trail completeness

    │
    ↓
[Alerting]
    │
    ├─ Critical Alerts (PagerDuty)
    │  ├─ Error rate > 5%
    │  ├─ Compliance violation
    │  └─ System outage
    │
    └─ Warning Alerts (Slack)
       ├─ P95 latency > 5 min
       ├─ Success rate < 90%
       └─ Cost spike detected
```

---

## Security & Compliance Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              SECURITY & COMPLIANCE                                          │
└─────────────────────────────────────────────────────────────────────────────┘

[Request]
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ AUTHENTICATION                                                              │
│ • AWS IAM (API Gateway)                                                     │
│ • OAuth2 (AgentCore Identity)                                               │
│ • JWT tokens                                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ├─ [FAIL] → Reject (401 Unauthorized)
    │
    └─ [PASS] ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ AUTHORIZATION                                                               │
│ • Role-based access control (RBAC)                                          │
│ • Permission checks                                                          │
│ • Resource-level access                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ├─ [FAIL] → Reject (403 Forbidden)
    │
    └─ [PASS] ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ DATA PROTECTION                                                             │
│ • TLS encryption (in transit)                                                │
│ • Encryption at rest (AgentCore Memory)                                     │
│ • PII detection & masking                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ AUDIT LOGGING                                                               │
│ • All agent actions logged                                                  │
│ • Patient data access tracked                                               │
│ • 7-year retention (HIPAA)                                                  │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
[COMPLIANCE VERIFIED]
```

---

## Scalability Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SCALABILITY ARCHITECTURE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

[Load]
    │
    │ 27,000 doctors × 20 patients/doctor = 540,000 patients
    │ 50,000+ appointments/day
    │ 1,000+ concurrent workflows
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ HORIZONTAL SCALING                                                          │
│                                                                             │
│ AgentCore Runtime:                                                          │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐                              │
│ │Session1│ │Session2│ │Session3│ │Session4│ ... (Auto-scales)             │
│ └────────┘ └────────┘ └────────┘ └────────┘                              │
│                                                                             │
│ Gateway:                                                                    │
│ ┌────────┐ ┌────────┐ ┌────────┐                                          │
│ │Gateway1│ │Gateway2│ │Gateway3│ (Load-balanced)                           │
│ └────────┘ └────────┘ └────────┘                                          │
│                                                                             │
│ Backend APIs:                                                               │
│ ┌────────┐ ┌────────┐ ┌────────┐                                          │
│ │  API1  │ │  API2  │ │  API3  │ (Independent scaling)                    │
│ └────────┘ └────────┘ └────────┘                                          │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│ CACHING STRATEGY                                                            │
│                                                                             │
│ AgentCore Memory:                                                           │
│ • Patient preferences (long-term)                                           │
│ • Provider availability (short-term)                                        │
│                                                                             │
│ API Gateway Cache:                                                          │
│ • Provider lists                                                            │
│ • Compliance rules                                                          │
│                                                                             │
│ CDN:                                                                        │
│ • Static knowledge base content                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Purpose**: Visual reference for CTO and Senior Architects

