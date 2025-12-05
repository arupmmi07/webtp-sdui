# Prompt-Driven Orchestration with LangFuse

## 🎯 **Overview**

This document explains the **Prompt-Driven Orchestration** architecture, which replaces hardcoded workflow logic with dynamic LLM-based orchestration using LangFuse prompts and tool calling.

---

## 📊 **Architecture Comparison**

### **Current: Code-Driven Orchestration**

```python
# Hardcoded workflow in langgraph_workflow.py
def reassignment_workflow():
    # Step 1: Get affected appointments (hardcoded)
    appointments = domain.get_affected_appointments(provider_id)
    
    # Step 2: For each appointment (hardcoded loop)
    for apt in appointments:
        # Step 3: Score providers (hardcoded scoring)
        scores = score_providers(apt, candidates)
        
        # Step 4: Assign best match (hardcoded threshold)
        if max(scores) >= 60:
            assign_to_provider(apt, best_provider)
        else:
            add_to_waitlist(apt)
```

**Problems:**
- ❌ Logic changes require code deployment
- ❌ Hard to test different strategies (A/B testing)
- ❌ Cannot adapt based on outcomes
- ❌ Tightly coupled to implementation
- ❌ No versioning of business logic

### **New: Prompt-Driven Orchestration**

```python
# Dynamic workflow driven by LangFuse prompts
orchestrator = PromptDrivenOrchestrator(
    domain_server=domain,
    patient_agent=patient_agent,
    booking_agent=booking_agent,
    use_langfuse=True
)

# LLM decides the workflow based on prompt
result = orchestrator.execute_workflow(
    provider_id="T001",
    date="2025-11-21",
    reason="sick"
)

# LLM will:
# 1. Call get_affected_appointments()
# 2. For each appointment:
#    - Call get_patient_details()
#    - Call get_available_providers()
#    - Call calculate_match_score() for each candidate
#    - Call assign_appointment() or add_to_waitlist()
# 3. Return structured summary
```

**Benefits:**
- ✅ Update logic by editing LangFuse prompts (no deployment!)
- ✅ A/B test strategies instantly (v1 vs v2)
- ✅ Adapt based on outcomes (reinforcement learning)
- ✅ Loosely coupled architecture
- ✅ Full versioning via LangFuse

---

## 🔧 **How It Works**

### **1. Define Tools (Python)**

Tools are Python functions that the LLM can call:

```python
class ToolRegistry:
    def get_affected_appointments(self, provider_id, date):
        # Implementation
        return {"appointments": [...], "count": 3}
    
    def calculate_match_score(self, patient_id, provider_id):
        # 6-factor scoring
        return {"score": 85, "factors": {...}}
    
    def assign_appointment(self, appointment_id, new_provider_id):
        # Book appointment
        return {"success": True}
```

### **2. Define Orchestration Logic (LangFuse Prompt)**

Store the logic in a LangFuse prompt:

```yaml
healthcare_orchestrator:
  prompt: |
    You are a Healthcare Operations Orchestrator AI.
    
    WORKFLOW STEPS:
    1. Get affected appointments for the unavailable provider
    2. For each appointment:
       a. Get patient details
       b. Get available providers
       c. Calculate match scores
       d. Select best match (score >= 60)
       e. Assign or add to waitlist
    3. Return summary
    
    DECISION CRITERIA:
    - Score >= 80: Excellent match, auto-assign
    - Score 60-79: Good match, assign with notification
    - Score < 60: Poor match, add to waitlist
```

### **3. LLM Orchestrates Using Tools**

The LLM reads the prompt and decides which tools to call:

```
Iteration 1:
  LLM: "I need to get affected appointments"
  Tool Call: get_affected_appointments(provider_id="T001", date="2025-11-21")
  Result: {"appointments": [A001, A002, A003], "count": 3}

Iteration 2:
  LLM: "I need patient details for A001"
  Tool Call: get_patient_details(patient_id="PAT001")
  Result: {"name": "Maria", "gender_preference": "female", ...}

Iteration 3:
  LLM: "I need available providers"
  Tool Call: get_available_providers(date="2025-11-21", specialty="orthopedic")
  Result: {"providers": [P001, P003], "count": 2}

Iteration 4:
  LLM: "Calculate match score for Maria + P001"
  Tool Call: calculate_match_score(patient_id="PAT001", provider_id="P001")
  Result: {"score": 150, "recommendation": "EXCELLENT"}

Iteration 5:
  LLM: "Score is excellent, I'll assign"
  Tool Call: assign_appointment(appointment_id="A001", new_provider_id="P001")
  Result: {"success": True}

... (continues for all appointments)

Final Response:
  {
    "total_affected": 3,
    "successful_assignments": 2,
    "waitlist_entries": 1,
    "assignments": [...]
  }
```

---

## 📈 **Key Benefits**

### **1. No-Code Logic Updates**

**Before:**
```python
# Change scoring logic → Edit code → Test → Deploy → Restart services
if gender_match:
    score += 15  # Want to change to 20? Need deployment!
```

**After:**
```yaml
# Change in LangFuse UI → Save → Instant effect (no deployment!)
scoring_strategy:
  prompt: |
    GENDER PREFERENCE: +20 points  # Changed from 15!
```

### **2. A/B Testing Different Strategies**

```python
# Test two strategies simultaneously
strategy_a = langfuse.get_prompt("scoring-strategy", label="v1")  # Conservative
strategy_b = langfuse.get_prompt("scoring-strategy", label="v2")  # Aggressive

# Route 50% of traffic to each
if random.random() < 0.5:
    use_strategy_a()
else:
    use_strategy_b()

# Analyze results in LangFuse dashboard
# Which strategy has better patient satisfaction? Lower HOD escalations?
```

### **3. Dynamic Adaptation**

```python
# System learns from outcomes
if outcomes['patient_satisfaction'] < 0.8:
    # Automatically switch to more conservative strategy
    strategy = langfuse.get_prompt("scoring-strategy", label="conservative")
else:
    # Use aggressive strategy for faster assignments
    strategy = langfuse.get_prompt("scoring-strategy", label="aggressive")
```

### **4. Full Versioning & Rollback**

```
LangFuse UI:
  v1.0 (Jan 1) - Original scoring
  v1.1 (Jan 15) - Increased gender preference weight
  v1.2 (Feb 1) - Added experience penalty for large gaps
  v1.3 (Feb 10) - BUG: Too conservative! → Rollback to v1.2 (instant!)
```

### **5. Observable & Debuggable**

Every LLM call is traced in LangFuse:
- Which prompt version was used?
- What tools were called?
- What was the reasoning?
- How long did it take?
- How much did it cost?

---

## 🎬 **Usage Examples**

### **Example 1: Basic Usage**

```python
from workflows.prompt_driven_orchestrator import create_prompt_driven_orchestrator

# Create orchestrator
orchestrator = create_prompt_driven_orchestrator(
    domain_server=json_domain_server,
    patient_engagement_agent=patient_agent,
    booking_agent=booking_agent,
    use_langfuse=True  # Use LangFuse prompts
)

# Execute workflow
result = orchestrator.execute_workflow(
    provider_id="T001",
    date="2025-11-21",
    reason="sick"
)

print(f"Assigned {result['successful_assignments']} patients")
print(f"Waitlist: {result['waitlist_entries']} patients")
```

### **Example 2: Custom LLM**

```python
from adapters.llm.litellm_adapter import LiteLLMAdapter

# Use specific LLM model
llm = LiteLLMAdapter(
    model="gpt-4o",  # More powerful model for complex decisions
    temperature=0.1  # More deterministic
)

orchestrator = create_prompt_driven_orchestrator(
    domain_server=domain,
    patient_agent=patient_agent,
    booking_agent=booking_agent,
    llm=llm,
    use_langfuse=True
)
```

### **Example 3: Local Prompts (No LangFuse)**

```python
# Works without LangFuse (uses local YAML file)
orchestrator = create_prompt_driven_orchestrator(
    domain_server=domain,
    patient_agent=patient_agent,
    booking_agent=booking_agent,
    use_langfuse=False  # Falls back to local prompts/langfuse_orchestrator_prompts.yaml
)
```

---

## 🧪 **Testing the Implementation**

### **Test Script**

```python
# test_prompt_orchestrator.py

from workflows.prompt_driven_orchestrator import create_prompt_driven_orchestrator
from mcp_servers.domain.json_domain_server import JSONDomainServer
from agents.patient_engagement_agent import PatientEngagementAgent
from agents.booking_agent import BookingAgent

def test_prompt_driven_workflow():
    # Setup
    domain = JSONDomainServer()
    patient_agent = PatientEngagementAgent(domain)
    booking_agent = BookingAgent(domain)
    
    # Create orchestrator
    orchestrator = create_prompt_driven_orchestrator(
        domain_server=domain,
        patient_engagement_agent=patient_agent,
        booking_agent=booking_agent,
        use_langfuse=False  # Use local prompts for testing
    )
    
    # Execute workflow
    result = orchestrator.execute_workflow(
        provider_id="T001",
        date="2025-11-21",
        reason="sick"
    )
    
    # Verify results
    assert result['total_affected'] == 3
    assert result['successful_assignments'] > 0
    print("✅ Test passed!")
    print(f"   Assignments: {result['successful_assignments']}")
    print(f"   Waitlist: {result['waitlist_entries']}")

if __name__ == "__main__":
    test_prompt_driven_workflow()
```

---

## 🔄 **Migration Strategy**

### **Phase 1: Parallel Running (Week 1)**

Run both systems side-by-side:

```python
# Use old system (code-driven)
old_result = langgraph_workflow.execute()

# Use new system (prompt-driven)
new_result = prompt_orchestrator.execute()

# Compare results
if old_result == new_result:
    print("✅ Results match!")
else:
    print("⚠️ Discrepancy detected, investigate")
    # Log for analysis
```

### **Phase 2: Gradual Rollout (Week 2-3)**

```python
# Route 10% traffic to new system
if random.random() < 0.1:
    use_prompt_orchestrator()
else:
    use_langgraph_workflow()

# Monitor metrics:
# - Success rate
# - Patient satisfaction
# - HOD escalations
# - Response time
```

### **Phase 3: Full Migration (Week 4)**

```python
# 100% traffic to new system
orchestrator = create_prompt_driven_orchestrator(...)
result = orchestrator.execute_workflow(...)

# Keep old system as fallback
# If new system fails → auto-fallback to old system
```

---

## 📊 **Performance Considerations**

### **Latency**

Prompt-driven orchestration may be slightly slower due to:
- Multiple LLM calls (one per tool decision)
- Network latency for LangFuse prompt fetching

**Mitigation:**
```python
# Cache LangFuse prompts
prompt_cache = {}
if "healthcare-orchestrator" not in prompt_cache:
    prompt_cache["healthcare-orchestrator"] = langfuse.get_prompt(...)

# Use faster LLM for orchestration
llm = LiteLLMAdapter(model="gpt-3.5-turbo")  # Faster, cheaper
```

### **Cost**

Each workflow execution = multiple LLM calls

**Estimation:**
- ~5-10 tool calls per patient
- ~500 tokens per call
- For 3 patients: ~15-30 calls = 7,500-15,000 tokens
- Cost (GPT-3.5): ~$0.02-0.04 per workflow
- Cost (Local LM Studio): $0.00 (free!)

### **Reliability**

LLM may make mistakes or call wrong tools

**Mitigation:**
```python
# Validate tool call results
def validate_result(tool_name, result):
    if tool_name == "calculate_match_score":
        assert 0 <= result['score'] <= 200, "Invalid score"
    # ... other validations

# Set max iterations to prevent infinite loops
max_iterations = 20

# Log all tool calls for debugging
logger.info(f"Tool: {tool_name}, Args: {args}, Result: {result}")
```

---

## 🎯 **When to Use Each Approach**

### **Use Code-Driven (LangGraph):**
- ✅ Well-defined, stable workflow
- ✅ Performance critical (< 100ms response)
- ✅ Deterministic behavior required
- ✅ Simple logic, few decision points

### **Use Prompt-Driven (LangFuse + Tools):**
- ✅ Evolving requirements
- ✅ Need frequent strategy updates
- ✅ A/B testing different approaches
- ✅ Complex decision-making
- ✅ Explainability important
- ✅ Learning from outcomes

---

## 📋 **Next Steps**

1. **Try it out:**
   ```bash
   python test_prompt_orchestrator.py
   ```

2. **Update prompts in LangFuse:**
   - Go to LangFuse UI
   - Create prompt: "healthcare-orchestrator"
   - Paste content from `prompts/langfuse_orchestrator_prompts.yaml`

3. **Set environment variables:**
   ```bash
   export LANGFUSE_PUBLIC_KEY="pk-..."
   export LANGFUSE_SECRET_KEY="sk-..."
   export LANGFUSE_HOST="https://cloud.langfuse.com"
   ```

4. **Integrate with API:**
   ```python
   # In api/server.py
   @app.post("/api/trigger-workflow-dynamic")
   async def trigger_dynamic_workflow(...):
       orchestrator = create_prompt_driven_orchestrator(...)
       return orchestrator.execute_workflow(...)
   ```

5. **Monitor in LangFuse:**
   - View all executions
   - Analyze tool usage patterns
   - Compare prompt versions
   - Track costs and latency

---

## 🚀 **Conclusion**

Prompt-driven orchestration represents the future of flexible, adaptive AI systems:

- **Agility:** Update logic without code deployment
- **Experimentation:** A/B test strategies safely
- **Observability:** Full tracing and debugging
- **Scalability:** Version control for business logic
- **Maintainability:** Simpler codebase

**The AI decides the workflow, not the code!** 🧠✨

