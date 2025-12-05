# AWS AgentCore Architecture - Executive Summary
## Quick Reference for CTO and Senior Architects

---

## 🎯 Key Questions Answered

### **Where is the Orchestrator?**
**Answer**: The **Supervisor Orchestrator Agent** runs on **Amazon Bedrock AgentCore Runtime** as a long-running agent session (up to 8 hours). It orchestrates the 6-stage workflow and coordinates specialized sub-agents.

**Key Points**:
- Fully-managed, serverless infrastructure
- No infrastructure to manage
- Auto-scales based on demand
- Complete session isolation for security

---

### **Where do Prompts Live?**
**Answer**: Prompts are managed in **LangFuse** (external prompt management platform) and fetched by AgentCore Runtime at runtime.

**Architecture**:
```
LangFuse (Prompt Management)
    ↓
AgentCore Runtime fetches prompts via API
    ↓
Prompts used by Supervisor Orchestrator Agent
```

**Benefits**:
- Version control and versioning
- A/B testing via labels (production, experiment-v1, experiment-v2)
- Cost tracking per prompt version
- No code changes needed to update prompts

**Example**:
```python
# AgentCore Runtime loads prompt from LangFuse
prompt = langfuse.get_prompt(
    "supervisor_orchestrator",
    label="production"  # or "experiment-v1" for A/B testing
)
```

---

### **How to Connect to Existing APIs?**
**Answer**: Use **AWS AgentCore Gateway** to transform existing REST APIs into MCP-compatible tools.

**Process**:
1. Register existing APIs in Gateway
2. Gateway automatically generates MCP tool definitions
3. Agents discover tools via semantic search
4. Gateway handles authentication, authorization, rate limiting

**Example Configuration**:
```yaml
gateway:
  mcp_servers:
    - name: "provider-api"
      type: "rest_api"
      base_url: "https://api.webpt.com/v1"
      tools:
        - get_provider
        - list_providers
        - check_availability
```

**Benefits**:
- Zero code changes to existing APIs
- Automatic tool discovery
- Built-in security and rate limiting
- Works with any REST API

---

### **How Does A/B Testing Work?**
**Answer**: A/B testing is handled via **LangFuse prompt labels** and **AgentCore Runtime traffic routing**.

**Flow**:
1. Create prompt variants in LangFuse with different labels:
   - `production` (80% traffic)
   - `experiment-v1` (20% traffic)
2. AgentCore Runtime routes workflows based on workflow_id:
   ```python
   if workflow_id % 2 == 0:
       label = "experiment-v1"  # 50% traffic
   else:
       label = "production"     # 50% traffic
   ```
3. Compare metrics in LangFuse dashboard:
   - Success rate
   - Latency
   - Cost per appointment
4. Promote winning variant to production

**Metrics Tracked**:
- Token usage per version
- Latency per version
- Success rate per version
- Cost per version

---

### **How to Ensure Quality & Guardrails?**
**Answer**: Multi-layer quality assurance with **Quality Assurance Agent** and **built-in guardrails**.

**Layers**:
1. **Schema Validation**: Validate JSON structure and types
2. **Compliance Checks**: POC requirements, payer rules, HIPAA
3. **Business Rules**: Distance constraints, availability, eligibility
4. **Risk Assessment**: No-show risk, continuity score, match quality

**Implementation**:
- **Quality Assurance Agent**: Validates outputs before actions
- **AgentCore Guardrails**: Built-in output validation, rate limiting, cost controls
- **Custom Validation**: Business-specific rules

**Example**:
```python
class QualityAssuranceAgent(Agent):
    async def validate_assignment(self, assignment):
        checks = [
            await self.check_compliance(assignment),
            await self.check_availability(assignment),
            await self.calculate_risk_score(assignment)
        ]
        
        if all(check.passed for check in checks):
            return Approval()
        else:
            return Rejection(reason="Failed checks")
```

---

### **How to Do Evaluations?**
**Answer**: Automated evaluation framework with **test scenarios** and **continuous monitoring**.

**Components**:
1. **Test Scenarios**: Golden dataset of 1000+ historical scenarios
2. **Automated Evaluations**: Daily runs on test dataset
3. **Metrics**: Success rate, compliance score, patient satisfaction
4. **Alerting**: Notify if metrics degrade

**Implementation**:
```python
class WorkflowEvaluator:
    async def evaluate(self, test_scenario):
        result = await orchestrator.execute(test_scenario)
        
        metrics = {
            "success_rate": self.calculate_success(result),
            "compliance_score": self.check_compliance(result),
            "patient_satisfaction": self.estimate_satisfaction(result)
        }
        
        return EvaluationResult(metrics=metrics)
```

**Continuous Evaluation**:
- Daily automated runs
- Compare against baseline
- Alert on regression
- Track improvements over time

---

## 📊 Architecture Components Summary

| Component | Location | Purpose |
|-----------|----------|---------|
| **Supervisor Orchestrator** | AgentCore Runtime | Main workflow orchestrator |
| **Specialized Agents** | AgentCore Runtime | Sub-agents for specific tasks |
| **Prompts** | LangFuse | Versioned, A/B testable prompts |
| **Memory** | AgentCore Memory | Short-term + long-term context |
| **API Integration** | AgentCore Gateway | Transforms REST APIs → MCP tools |
| **Observability** | AgentCore + LangFuse | Monitoring, tracing, analytics |
| **Quality Assurance** | Quality Assurance Agent | Validates outputs before actions |
| **Guardrails** | AgentCore Built-in | Output validation, rate limiting |

---

## 🔄 Workflow Trigger Flow

```
1. External System (EHR/Calendar/Admin Portal)
   ↓
2. AWS API Gateway (Authentication, Rate Limiting)
   ↓
3. AgentCore Runtime (Creates new session)
   ↓
4. Supervisor Orchestrator Agent (Orchestrates 6 stages)
   ↓
5. Specialized Agents (Execute specific tasks)
   ↓
6. AgentCore Gateway (Calls existing APIs via MCP)
   ↓
7. Existing Backend Systems (Provider/Patient/Appointment APIs)
   ↓
8. Results returned to Supervisor Orchestrator
   ↓
9. Audit & Reporting
   ↓
10. Workflow Complete
```

---

## 🎯 Key Benefits

### **1. Zero Infrastructure Management**
- Fully-managed AgentCore Runtime
- Auto-scaling based on demand
- No servers to manage
- Pay only for usage

### **2. Framework Flexibility**
- Works with LangGraph, CrewAI, or any framework
- Use any Bedrock model (Claude, GPT, etc.)
- Easy to swap frameworks/models

### **3. Secure API Integration**
- Gateway handles authentication/authorization
- No code changes to existing APIs
- Automatic tool discovery
- Built-in rate limiting

### **4. Production Observability**
- AgentCore Observability (CloudWatch)
- LangFuse analytics (prompts, costs)
- Custom dashboards (business metrics)
- Complete audit trail

### **5. Quality & Compliance**
- Multi-layer guardrails
- Automated quality assurance
- Compliance validation
- Risk assessment

### **6. A/B Testing & Experimentation**
- Easy prompt A/B testing via LangFuse
- Traffic splitting
- Metrics comparison
- Gradual rollout

---

## 📈 Scalability

**Design Target**:
- **27,000 doctors**
- **~500,000 patients** (20 patients/doctor average)
- **1,000+ concurrent workflows**
- **50,000+ appointments/day**

**Scaling Strategy**:
- **Horizontal**: AgentCore Runtime auto-scales
- **Caching**: AgentCore Memory + API Gateway cache
- **Load Balancing**: Gateway load-balanced across instances
- **Database**: Read replicas, partitioning, indexing

---

## 🔒 Security & Compliance

### **Authentication & Authorization**
- AWS IAM (API Gateway)
- OAuth2 (AgentCore Identity)
- JWT tokens
- Role-based access control (RBAC)

### **Data Protection**
- TLS encryption (in transit)
- Encryption at rest (AgentCore Memory)
- PII detection & masking
- Complete audit trail

### **Compliance**
- HIPAA compliant
- SOC 2 compliant
- 7-year audit retention
- Data residency controls

---

## 💰 Cost Optimization

### **Token Usage**
- Prompt optimization (shorter prompts)
- Caching LLM responses
- Model selection (smaller models for simple tasks)

### **API Calls**
- Batch operations
- Caching in AgentCore Memory
- Rate limiting

### **Infrastructure**
- Serverless (pay per use)
- Reserved capacity (predictable workloads)
- Cost monitoring (CloudWatch alerts)

---

## 🚀 Migration Path

### **Phase 1: Proof of Concept (Weeks 1-4)**
- Deploy Supervisor Orchestrator on AgentCore Runtime
- Connect 1-2 existing APIs via Gateway
- Test with 100 appointments

### **Phase 2: Pilot (Weeks 5-8)**
- Expand to 1,000 doctors
- Integrate all APIs via Gateway
- Enable observability and monitoring

### **Phase 3: Production Rollout (Weeks 9-12)**
- Gradual rollout to all 27,000 doctors
- Enable A/B testing
- Continuous evaluation and optimization

---

## 📚 Documentation References

1. **AGENTCORE_ARCHITECTURE.md**: Detailed architecture documentation
2. **AGENTCORE_FLOW_DIAGRAM.md**: Visual flow diagrams
3. **AWS AgentCore Documentation**: https://aws.amazon.com/bedrock/agentcore/
4. **LangFuse Documentation**: https://langfuse.com/docs

---

## 🎓 Key Takeaways

1. **Orchestrator**: Runs on AgentCore Runtime as a long-running agent session
2. **Prompts**: Managed in LangFuse, fetched at runtime, A/B testable
3. **API Integration**: AgentCore Gateway transforms REST APIs → MCP tools
4. **Quality**: Multi-layer guardrails + Quality Assurance Agent
5. **Observability**: AgentCore + LangFuse for comprehensive monitoring
6. **Scalability**: Auto-scaling, caching, load balancing
7. **Security**: Enterprise-grade security and compliance built-in

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Audience**: CTO, Senior Architects

