# AWS AgentCore Production Architecture
## Scalable Agentic AI System for 27,000 Doctors & Patients

---

## Executive Summary

This document outlines a production-ready, enterprise-scale architecture leveraging **Amazon Bedrock AgentCore** to orchestrate intelligent appointment rescheduling workflows. The system is designed to handle **27,000 doctors and their patients** with enterprise-grade security, observability, and scalability.

**Key Capabilities:**
- **Zero Infrastructure Management**: Fully-managed AgentCore services
- **Framework Flexibility**: Works with LangGraph, CrewAI, or any agent framework
- **Secure API Integration**: AWS Gateway transforms existing APIs into MCP-compatible tools
- **Production Observability**: Comprehensive monitoring, A/B testing, and quality gates
- **Long-Running Workflows**: Support for 8-hour asynchronous agent tasks

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EXTERNAL TRIGGERS                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ EHR System   │  │ Calendar    │  │ Admin Portal │  │ Patient API  │    │
│  │ (WebPT/      │  │ Integration │  │ (Manual)     │  │ (Mobile App) │    │
│  │  Athena)     │  │             │  │              │  │              │    │
│  └──────┬───────┘  └──────┬──────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │                 │             │
│         └─────────────────┴─────────────────┴─────────────────┘             │
│                                    │                                         │
│                                    ↓                                         │
│                    ┌───────────────────────────────┐                        │
│                    │   AWS API Gateway             │                        │
│                    │   (Workflow Trigger Endpoint) │                        │
│                    └───────────────┬───────────────┘                        │
└────────────────────────────────────┼─────────────────────────────────────────┘
                                    │
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AMAZON BEDROCK AGENTCORE RUNTIME                         │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    SUPERVISOR ORCHESTRATOR AGENT                    │   │
│  │  (Deployed on AgentCore Runtime - Long-Running Session)            │   │
│  │                                                                     │   │
│  │  Responsibilities:                                                  │   │
│  │  • Workflow orchestration (6-stage process)                         │   │
│  │  • Agent coordination (multi-agent communication)                  │   │
│  │  • Error handling & retries                                        │   │
│  │  • Session state management                                         │   │
│  │  • Guardrail enforcement                                            │   │
│  │                                                                     │   │
│  │  Prompts: Managed in LangFuse (versioned, A/B testable)            │   │
│  │  Memory: AgentCore Memory (short-term + long-term context)         │   │
│  └───────────────────┬───────────────────────────────────────────────┘   │
│                      │                                                      │
│         ┌────────────┼────────────┬──────────────┬──────────────┐         │
│         ↓            ↓            ↓              ↓              ↓          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Smart    │ │ Patient  │ │ Backfill │ │ Quality  │ │ Audit    │         │
│  │ Scheduling│ │Engagement│ │  Agent   │ │ Assurance │ │  Agent   │         │
│  │  Agent   │ │  Agent   │ │          │ │  Agent    │ │          │         │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘         │
│       │            │            │            │            │                │
│       └────────────┴────────────┴────────────┴────────────┘                │
│                      │                                                      │
│                      ↓                                                       │
│  ┌──────────────────────────────────────────────────────────────┐          │
│  │              AGENTCORE GATEWAY (MCP Integration)              │          │
│  │                                                               │          │
│  │  Transforms existing APIs into agent-compatible tools:        │          │
│  │  • Provider API → get_provider, list_providers, etc.         │          │
│  │  • Patient API → get_patient, get_preferences, etc.         │          │
│  │  • Appointment API → get_appointment, update_appointment     │          │
│  │  • Notification API → send_email, send_sms, send_ivr         │          │
│  │  • Waitlist API → add_to_waitlist, query_waitlist            │          │
│  │  • Knowledge API → search_compliance_rules, get_payer_rules  │          │
│  └───────────────────────────┬───────────────────────────────────┘          │
└──────────────────────────────┼──────────────────────────────────────────────┘
                               │
                               ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    EXISTING BACKEND SYSTEMS (via Gateway)                   │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Provider     │  │ Patient      │  │ Appointment   │  │ Notification  │  │
│  │ Management   │  │ Management   │  │ Scheduling   │  │ Services      │  │
│  │ API          │  │ API          │  │ API          │  │ (SMS/Email)   │  │
│  │              │  │              │  │              │  │               │  │
│  │ (WebPT/      │  │ (EHR/        │  │ (Calendar/   │  │ (Twilio/     │  │
│  │  Athena)     │  │  Custom)     │  │  Scheduling) │  │  SendGrid)    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                                             │
│  ┌──────────────┐  ┌──────────────┐                                      │
│  │ Waitlist     │  │ Knowledge     │                                      │
│  │ Management   │  │ Base          │                                      │
│  │ API          │  │ (Compliance/ │                                      │
│  │              │  │  Payer Rules) │                                      │
│  └──────────────┘  └──────────────┘                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. AWS API Gateway (Trigger Layer)

**Purpose**: Entry point for all workflow triggers

**Responsibilities**:
- Receive triggers from EHR systems, calendar integrations, admin portals
- Authenticate and authorize requests (OAuth2/JWT)
- Route to appropriate AgentCore Runtime session
- Rate limiting and throttling

**Configuration**:
```yaml
# API Gateway Configuration
endpoints:
  - /api/workflow/trigger
    method: POST
    auth: AWS_IAM + OAuth2
    rate_limit: 1000 req/min
    integration: AgentCore Runtime (async)
```

**Trigger Types**:
- `provider_unavailable`: Doctor departure/unavailability
- `patient_reschedule_request`: Patient-initiated rescheduling
- `appointment_cancellation`: Cancellation with backfill
- `emergency_reassignment`: Urgent reassignment needs

---

### 2. Amazon Bedrock AgentCore Runtime

**Purpose**: Secure, serverless infrastructure for agent execution

**Key Features**:
- **Session Isolation**: Complete isolation between workflow sessions
- **Long-Running Support**: Up to 8 hours for complex multi-step workflows
- **Low Latency**: Sub-second response times for real-time interactions
- **Auto-Scaling**: Handles concurrent workflows automatically

**Deployment**:
```python
# Supervisor Orchestrator Agent (deployed on AgentCore Runtime)
from agentcore import Agent, Runtime

class SupervisorOrchestratorAgent(Agent):
    """Main orchestrator agent running on AgentCore Runtime."""
    
    def __init__(self):
        super().__init__(
            name="supervisor_orchestrator",
            model="anthropic.claude-sonnet-4",  # Any Bedrock model
            memory_enabled=True,  # AgentCore Memory
            tools=[],  # Tools registered via Gateway
            max_runtime_hours=8
        )
    
    async def execute(self, trigger_event):
        """Orchestrate 6-stage workflow."""
        # Stage 1: Trigger Detection
        affected_appointments = await self.trigger_handler(trigger_event)
        
        # Stage 2-6: Orchestrate via sub-agents
        results = await self.orchestrate_workflow(affected_appointments)
        
        return results
```

**Session Management**:
- Each workflow execution = 1 AgentCore Runtime session
- Session ID tracks entire workflow lifecycle
- State persisted in AgentCore Memory
- Supports checkpointing and resumption

---

### 3. Supervisor Orchestrator Agent

**Location**: Deployed as an agent on AgentCore Runtime

**Responsibilities**:
1. **Workflow Orchestration**: Coordinates 6-stage appointment rescheduling process
2. **Agent Coordination**: Manages communication between specialized agents
3. **Error Handling**: Retries, fallbacks, escalation
4. **Guardrail Enforcement**: Validates outputs before actions
5. **State Management**: Maintains workflow state across stages

**Prompt Management**:
- **Storage**: LangFuse (external prompt management)
- **Versioning**: LangFuse handles prompt versions
- **A/B Testing**: LangFuse labels (production, staging, experiment-v1, experiment-v2)
- **Access**: AgentCore Runtime fetches prompts via LangFuse API

```python
# Prompt Loading (from LangFuse)
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
)

# Load prompt with A/B testing label
prompt = langfuse.get_prompt(
    "supervisor_orchestrator",
    label="production"  # or "experiment-v2" for A/B testing
)

# Use in agent
agent.system_prompt = prompt.prompt
```

**Memory Management**:
- **Short-Term Memory**: AgentCore Memory (session-scoped)
- **Long-Term Memory**: AgentCore Memory (cross-session, patient preferences)
- **Knowledge Base**: Compliance rules, payer policies (via Gateway)

---

### 4. Specialized Agents (Sub-Agents)

All agents run on AgentCore Runtime and communicate via AgentCore's built-in agent-to-agent messaging.

#### 4.1 Smart Scheduling Agent
- **Purpose**: Provider matching, filtering, scoring
- **Tools**: Provider API, Knowledge API (compliance rules)
- **Output**: Ranked provider recommendations

#### 4.2 Patient Engagement Agent
- **Purpose**: Patient communication, consent management
- **Tools**: Notification API (email/SMS/IVR), Patient API
- **Output**: Patient responses, consent status

#### 4.3 Backfill Agent
- **Purpose**: Fill freed slots, waitlist management
- **Tools**: Waitlist API, Appointment API
- **Output**: Backfill assignments

#### 4.4 Quality Assurance Agent
- **Purpose**: Validate outputs, enforce guardrails
- **Tools**: Knowledge API (compliance rules), Risk Calculator
- **Output**: Approval/rejection with reasoning

#### 4.5 Audit Agent
- **Purpose**: Generate audit logs, compliance reports
- **Tools**: Audit API, Reporting API
- **Output**: Complete audit trail

---

### 5. AWS AgentCore Gateway (MCP Integration)

**Purpose**: Transform existing APIs into agent-compatible tools

**How It Works**:
1. **API Discovery**: Gateway discovers existing REST APIs
2. **Tool Generation**: Automatically generates MCP-compatible tool definitions
3. **Semantic Search**: Enables intelligent tool discovery via semantic search
4. **Security**: Handles authentication, authorization, rate limiting

**Configuration**:
```yaml
# Gateway Configuration (MCP Server Registration)
gateway:
  mcp_servers:
    - name: "provider-api"
      type: "rest_api"
      base_url: "https://api.webpt.com/v1"
      authentication:
        type: "oauth2"
        credentials: "${WEBPT_OAUTH_TOKEN}"
      tools:
        - get_provider
        - list_providers
        - check_availability
    
    - name: "patient-api"
      type: "rest_api"
      base_url: "https://api.ehr.com/v1"
      authentication:
        type: "api_key"
        credentials: "${EHR_API_KEY}"
      tools:
        - get_patient
        - get_preferences
        - update_patient
    
    - name: "knowledge-base"
      type: "mcp_server"
      endpoint: "https://mcp.knowledge.internal"
      tools:
        - search_compliance_rules
        - get_payer_rules
        - get_scoring_weights
```

**Tool Registration**:
```python
# Agents automatically discover tools via Gateway
# No manual tool registration needed!

# Agent uses tool via semantic search
result = await agent.use_tool(
    "Find providers matching patient specialty",
    # Gateway automatically routes to correct API
    # and transforms response to agent-readable format
)
```

---

### 6. AgentCore Memory

**Purpose**: Persistent context across interactions

**Types**:
- **Short-Term Memory**: Session-scoped (workflow execution)
- **Long-Term Memory**: Cross-session (patient preferences, provider history)

**Usage**:
```python
# Store patient preferences (long-term)
await agent.memory.store(
    key="patient_preferences:${patient_id}",
    value={
        "preferred_providers": ["P001", "P004"],
        "communication_preference": "email",
        "max_distance": 10
    },
    ttl=None  # Permanent
)

# Retrieve in future sessions
preferences = await agent.memory.retrieve("patient_preferences:${patient_id}")
```

**Benefits**:
- Reduces redundant API calls
- Personalizes patient experience
- Maintains continuity across workflows

---

### 7. Observability & Monitoring

#### 7.1 AgentCore Observability
- **Built-in Dashboards**: CloudWatch integration
- **Metrics**: Token usage, latency, session duration, error rates
- **Traces**: Complete agent workflow traces
- **Debugging**: Session replay, step-by-step execution

#### 7.2 LangFuse Integration
- **Prompt Versioning**: Track prompt changes
- **A/B Testing**: Compare prompt variations
- **Cost Tracking**: Token usage per prompt version
- **Performance Analytics**: Latency, success rates

#### 7.3 Custom Monitoring
- **Business Metrics**: Appointments processed, success rate, patient satisfaction
- **Compliance Metrics**: POC validation rate, payer rule violations
- **Alerting**: PagerDuty/Slack integration for critical issues

---

### 8. Quality Assurance & Guardrails

#### 8.1 Quality Assurance Agent
**Purpose**: Validate agent outputs before taking actions

**Validation Rules**:
1. **Compliance Checks**: POC validation, payer rules
2. **Data Quality**: Provider availability, patient eligibility
3. **Business Rules**: Specialty matching, distance constraints
4. **Risk Assessment**: No-show risk, continuity score

**Implementation**:
```python
class QualityAssuranceAgent(Agent):
    async def validate_assignment(self, assignment):
        """Validate provider assignment before booking."""
        checks = [
            await self.check_compliance(assignment),
            await self.check_availability(assignment),
            await self.check_distance_constraints(assignment),
            await self.calculate_risk_score(assignment)
        ]
        
        if all(check.passed for check in checks):
            return Approval(reason="All checks passed")
        else:
            return Rejection(
                reason="Failed checks: " + ", ".join(
                    check.reason for check in checks if not check.passed
                )
            )
```

#### 8.2 Guardrails
- **Output Validation**: Schema validation for all agent outputs
- **Rate Limiting**: Prevent API abuse
- **Cost Controls**: Token usage limits per workflow
- **Safety Filters**: Content moderation, PII detection

**Configuration**:
```yaml
guardrails:
  output_validation:
    enabled: true
    schema: "appointment_assignment_schema.json"
  
  rate_limiting:
    max_api_calls_per_minute: 100
    max_tokens_per_workflow: 50000
  
  safety_filters:
    pii_detection: true
    content_moderation: true
```

---

### 9. A/B Testing & Experimentation

#### 9.1 Prompt A/B Testing (LangFuse)
```python
# Deploy experiment variant
experiment_prompt = langfuse.get_prompt(
    "supervisor_orchestrator",
    label="experiment-v2"  # New prompt version
)

# Route traffic
if workflow_id % 2 == 0:
    # 50% to experiment
    agent.system_prompt = experiment_prompt.prompt
else:
    # 50% to production
    agent.system_prompt = production_prompt.prompt

# Compare metrics in LangFuse dashboard
```

#### 9.2 Agent Strategy A/B Testing
- **Variant A**: Conservative matching (higher continuity score threshold)
- **Variant B**: Aggressive matching (lower threshold, faster assignment)
- **Metrics**: Success rate, patient satisfaction, time-to-assignment

#### 9.3 Feature Flags
```python
# Feature flag configuration
feature_flags:
  enable_ai_scoring: true
  enable_backfill_automation: true
  enable_patient_preferences: false  # Experimenting
```

---

### 10. Evaluations & Testing

#### 10.1 Automated Evaluations
**Purpose**: Continuously validate agent performance

**Evaluation Types**:
1. **Unit Tests**: Individual agent functions
2. **Integration Tests**: End-to-end workflows
3. **Regression Tests**: Historical scenarios
4. **Compliance Tests**: Payer rules, HIPAA

**Implementation**:
```python
# Evaluation Framework
class WorkflowEvaluator:
    async def evaluate(self, test_scenario):
        """Run evaluation on test scenario."""
        result = await orchestrator.execute(test_scenario)
        
        metrics = {
            "success_rate": self.calculate_success(result),
            "compliance_score": self.check_compliance(result),
            "patient_satisfaction": self.estimate_satisfaction(result),
            "time_to_resolution": result.duration
        }
        
        return EvaluationResult(metrics=metrics)
```

#### 10.2 Test Scenarios
- **Golden Dataset**: 1000+ historical appointment rescheduling scenarios
- **Edge Cases**: Complex payer rules, multiple constraints
- **Stress Tests**: High concurrency, API failures

#### 10.3 Continuous Evaluation
- **Daily Runs**: Automated evaluation on test dataset
- **Alerting**: Notify if metrics degrade
- **Regression Detection**: Compare against baseline

---

## Workflow Execution Flow

### Appointment Rescheduling Workflow (6 Stages)

```
1. TRIGGER DETECTION
   ├─ Input: Provider unavailable event
   ├─ Agent: Smart Scheduling Agent
   ├─ Tools: Provider API, Appointment API
   └─ Output: Affected appointments list

2. CANDIDATE FILTERING
   ├─ Input: Affected appointments + All providers
   ├─ Agent: Smart Scheduling Agent
   ├─ Tools: Knowledge API (compliance rules), Provider API
   └─ Output: Qualified providers (3-5 per appointment)

3. SCORING & RANKING
   ├─ Input: Qualified providers + Patient profiles
   ├─ Agent: Smart Scheduling Agent
   ├─ Tools: Knowledge API (scoring weights), Patient API
   ├─ LLM: Provider scoring (continuity, specialty, location, etc.)
   └─ Output: Ranked providers (top 3)

4. QUALITY ASSURANCE
   ├─ Input: Top-ranked provider assignments
   ├─ Agent: Quality Assurance Agent
   ├─ Tools: Knowledge API (guardrails), Risk Calculator
   └─ Output: Approved assignments (or rejections with reasons)

5. PATIENT CONSENT
   ├─ Input: Approved assignments
   ├─ Agent: Patient Engagement Agent
   ├─ Tools: Notification API (email/SMS), Patient API
   └─ Output: Patient responses (accept/decline)

6. BOOKING & BACKFILL
   ├─ Input: Accepted assignments + Declined appointments
   ├─ Agent: Backfill Agent + Smart Scheduling Agent
   ├─ Tools: Appointment API, Waitlist API
   └─ Output: Booked appointments + Backfilled slots

7. AUDIT & REPORTING
   ├─ Input: Complete workflow data
   ├─ Agent: Audit Agent
   ├─ Tools: Audit API, Reporting API
   └─ Output: Audit log + Compliance report
```

---

## Scalability Considerations

### Current Capacity (Design Target)
- **Doctors**: 27,000
- **Patients**: ~500,000 (assuming 20 patients per doctor average)
- **Concurrent Workflows**: 1,000+
- **Daily Appointments Processed**: 50,000+

### Scaling Strategy

#### Horizontal Scaling
- **AgentCore Runtime**: Auto-scales based on demand
- **Gateway**: Load-balanced across multiple instances
- **Backend APIs**: Scale independently

#### Caching Strategy
- **AgentCore Memory**: Cache patient preferences, provider availability
- **API Gateway**: Cache frequently accessed data (provider lists)
- **CDN**: Cache static knowledge base content

#### Database Optimization
- **Read Replicas**: For high-read workloads (provider queries)
- **Partitioning**: Partition by provider/patient ID
- **Indexing**: Optimize for common query patterns

---

## Security & Compliance

### Authentication & Authorization
- **AgentCore Identity**: OAuth2 integration with existing identity provider
- **API Gateway**: AWS IAM + OAuth2
- **Backend APIs**: Existing authentication (preserved via Gateway)

### Data Protection
- **Encryption**: TLS in transit, encryption at rest
- **PII Handling**: AgentCore Memory encrypts sensitive data
- **Access Control**: Role-based access (RBAC)

### Compliance
- **HIPAA**: Complete audit trail, data retention policies
- **SOC 2**: AgentCore is SOC 2 compliant
- **GDPR**: Data residency controls, right to deletion

### Audit Logging
- **AgentCore Observability**: All agent actions logged
- **Custom Audit**: Compliance-specific logging
- **Retention**: 7-year retention per HIPAA

---

## Cost Optimization

### Token Usage
- **Prompt Optimization**: Shorter prompts, template-driven
- **Caching**: Cache LLM responses for similar scenarios
- **Model Selection**: Use smaller models for simple tasks

### API Calls
- **Batch Operations**: Batch provider queries
- **Caching**: Cache provider/patient data in AgentCore Memory
- **Rate Limiting**: Prevent unnecessary API calls

### Infrastructure
- **Serverless**: Pay only for actual usage (AgentCore Runtime)
- **Reserved Capacity**: For predictable workloads
- **Cost Monitoring**: CloudWatch cost alerts

---

## Migration Path

### Phase 1: Proof of Concept (Weeks 1-4)
- Deploy Supervisor Orchestrator on AgentCore Runtime
- Connect 1-2 existing APIs via Gateway
- Test with 100 appointments

### Phase 2: Pilot (Weeks 5-8)
- Expand to 1,000 doctors
- Integrate all APIs via Gateway
- Enable observability and monitoring

### Phase 3: Production Rollout (Weeks 9-12)
- Gradual rollout to all 27,000 doctors
- Enable A/B testing
- Continuous evaluation and optimization

---

## Monitoring & Alerting

### Key Metrics

#### System Metrics
- **Agent Execution Time**: P50, P95, P99 latencies
- **Token Usage**: Tokens per workflow, cost per appointment
- **Error Rate**: Failed workflows, API errors
- **Session Duration**: Average workflow completion time

#### Business Metrics
- **Appointments Processed**: Daily/weekly counts
- **Success Rate**: % of appointments successfully reassigned
- **Patient Satisfaction**: Response rates, acceptance rates
- **Time to Resolution**: Average time from trigger to booking

#### Compliance Metrics
- **POC Validation Rate**: % of assignments passing POC checks
- **Payer Rule Compliance**: Violations per day
- **Audit Trail Completeness**: % of workflows with complete audit logs

### Alerting Rules
```yaml
alerts:
  - name: "High Error Rate"
    condition: "error_rate > 5%"
    severity: "critical"
    channel: "pagerduty"
  
  - name: "Slow Workflow Execution"
    condition: "p95_latency > 5 minutes"
    severity: "warning"
    channel: "slack"
  
  - name: "Compliance Violation"
    condition: "payer_rule_violations > 0"
    severity: "critical"
    channel: "pagerduty"
```

---

## Conclusion

This architecture provides a **production-ready, scalable foundation** for deploying agentic AI workflows at enterprise scale. By leveraging AWS AgentCore's fully-managed services, we eliminate infrastructure complexity while maintaining:

- **Flexibility**: Works with any framework, any model
- **Security**: Enterprise-grade security and compliance
- **Observability**: Comprehensive monitoring and debugging
- **Scalability**: Handles 27,000+ doctors and millions of patients
- **Quality**: Built-in guardrails, A/B testing, evaluations

The system is designed to evolve with your needs, supporting gradual migration from existing systems while maintaining backward compatibility.

---

## Appendix: Configuration Examples

### AgentCore Runtime Configuration
```yaml
runtime:
  name: "supervisor_orchestrator"
  model: "anthropic.claude-sonnet-4"
  memory:
    enabled: true
    type: "short_term_and_long_term"
  max_runtime_hours: 8
  session_isolation: true
  vpc_config:
    subnet_ids: ["subnet-xxx"]
    security_group_ids: ["sg-xxx"]
```

### Gateway MCP Server Registration
```yaml
gateway:
  mcp_servers:
    - name: "provider-api"
      type: "rest_api"
      base_url: "${PROVIDER_API_URL}"
      authentication:
        type: "oauth2"
      tools:
        - name: "get_provider"
          method: "GET"
          path: "/providers/{provider_id}"
        - name: "list_providers"
          method: "GET"
          path: "/providers"
          query_params:
            - specialty
            - location
            - availability
```

### LangFuse Prompt Configuration
```yaml
prompts:
  supervisor_orchestrator:
    name: "supervisor_orchestrator"
    labels:
      production: "v2.1"
      staging: "v2.2"
      experiment-v1: "v3.0-beta"
    a_b_testing:
      enabled: true
      traffic_split:
        production: 80
        experiment-v1: 20
```

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Author**: Architecture Team  
**Reviewers**: CTO, Senior Architects

