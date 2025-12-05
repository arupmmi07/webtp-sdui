# LangGraph Workflow Diagram

## Visual Workflow Graph with Conditional Branching

```
                     START
                       ↓
                ┌──────────────┐
                │   TRIGGER    │
                │ Find affected│
                │ appointments │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │    FILTER    │
                │ Apply 4 core │
                │    filters   │
                └──────┬───────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
    Candidates                    No candidates
      found                           found
        │                             │
        ↓                             ↓
  ┌──────────────┐            ┌──────────────┐
  │    SCORE     │            │ HOD FALLBACK │
  │ Rank by 5    │            │ Assign to    │
  │   factors    │            │ Head of Dept │
  └──────┬───────┘            └──────┬───────┘
         │                           │
         ↓                           │
  ┌──────────────┐                   │
  │   CONSENT    │                   │
  │ Email patient│                   │
  │  with offer  │                   │
  └──────┬───────┘                   │
         │                           │
    ┌────┴────┐                      │
    │         │                      │
  Patient   Patient                  │
  says YES  says NO                  │
    │         │                      │
    │         ↓                      │
    │  ┌──────────────┐              │
    │  │NEXT PROVIDER │              │
    │  │ Try provider │              │
    │  │  #2, #3, etc │              │
    │  └──────┬───────┘              │
    │         │                      │
    │    ┌────┴─────┐                │
    │    │          │                │
    │  More      No more             │
    │providers  providers            │
    │    │          │                │
    │    │          ↓                │
    │    │   ┌──────────────┐        │
    │    │   │ HOD FALLBACK │        │
    │    │   │   or MANUAL  │        │
    │    │   │    REVIEW    │        │
    │    │   └──────┬───────┘        │
    │    │          │                │
    │    └──────────┤                │
    │               │                │
    ↓               ↓                ↓
┌────────────────────────────────────┐
│             BOOK                   │
│ Confirm appointment & notify       │
└────────────────┬───────────────────┘
                 ↓
         ┌──────────────┐
         │    AUDIT     │
         │ Generate log │
         └──────┬───────┘
                ↓
               END
```

---

## Decision Points (Conditional Branches)

### 1️⃣ After FILTER: Candidates Found?

```python
def _route_after_filter(state):
    if len(state["qualified_providers"]) > 0:
        return "score"  # ✅ Continue with scoring
    else:
        return "hod_fallback"  # ❌ No candidates, escalate to HOD
```

**Example:**
- ✅ 2 candidates found (P001, P004) → Go to SCORE
- ❌ 0 candidates found (all eliminated) → Go to HOD_FALLBACK

---

### 2️⃣ After CONSENT: Patient Response?

```python
def _route_after_consent(state):
    response = state["patient_response"]
    
    if response == "YES":
        return "book"  # ✅ Patient approved, book it
    elif response == "NO":
        return "next_provider"  # ❌ Try next ranked provider
    else:
        return "manual_review"  # ⚠️ Timeout or error
```

**Example:**
- ✅ Maria says "YES" → Go to BOOK
- ❌ Maria says "NO" → Go to NEXT_PROVIDER
- ⏰ Maria doesn't respond (timeout) → Go to MANUAL_REVIEW

---

### 3️⃣ After NEXT_PROVIDER: More Providers to Try?

```python
def _route_after_next_provider(state):
    current_index = state["current_provider_index"]
    total_providers = len(state["ranked_providers"])
    offers_sent = state["offers_sent"]
    
    if current_index < total_providers:
        return "score"  # ✅ Try next provider
    elif offers_sent < 3:
        return "hod_fallback"  # ❌ All tried, go to HOD
    else:
        return "manual_review"  # ❌ Max retries, manual review
```

**Example:**
- ✅ Provider #2 available → Go to SCORE (offer Dr. Michael Lee)
- ❌ All providers tried → Go to HOD_FALLBACK
- ⚠️ 3+ offers sent → Go to MANUAL_REVIEW

---

## Real-World Scenarios

### Scenario A: Happy Path (Patient Says YES)

```
START → TRIGGER → FILTER (2 found) → SCORE (#1: Dr. Ross)
  → CONSENT (email sent) → [Maria says YES]
  → BOOK (confirmed) → AUDIT → END
```

**Result:** ✅ Appointment confirmed in 30 seconds

---

### Scenario B: Patient Declines (Try Next Provider)

```
START → TRIGGER → FILTER (2 found) → SCORE (#1: Dr. Ross)
  → CONSENT (email sent) → [Maria says NO]
  → NEXT_PROVIDER (#2: Dr. Lee) → SCORE (#2: Dr. Lee)
  → CONSENT (email sent) → [Maria says YES]
  → BOOK (confirmed) → AUDIT → END
```

**Result:** ✅ Second provider worked (took 2 offers)

---

### Scenario C: All Providers Declined (HOD Fallback)

```
START → TRIGGER → FILTER (2 found) → SCORE (#1: Dr. Ross)
  → CONSENT (email sent) → [Maria says NO]
  → NEXT_PROVIDER (#2: Dr. Lee) → SCORE (#2: Dr. Lee)
  → CONSENT (email sent) → [Maria says NO]
  → NEXT_PROVIDER (no more) → HOD_FALLBACK (Dr. Williams)
  → BOOK (confirmed) → AUDIT → END
```

**Result:** ✅ HOD assigned automatically

---

### Scenario D: No Qualified Candidates (Skip to HOD)

```
START → TRIGGER → FILTER (0 found - all eliminated)
  → HOD_FALLBACK (Dr. Williams assigned)
  → BOOK (confirmed) → AUDIT → END
```

**Result:** ✅ Direct escalation to HOD

---

### Scenario E: Patient Timeout (Manual Review)

```
START → TRIGGER → FILTER (2 found) → SCORE (#1: Dr. Ross)
  → CONSENT (email sent) → [No response after 24h]
  → MANUAL_REVIEW → END
```

**Result:** ⚠️ Front desk needs to call patient manually

---

## State Management Example

### Initial State:
```python
{
    "therapist_id": "T001",
    "current_provider_index": 0,
    "offers_sent": 0,
    "ranked_providers": [
        {"provider_id": "P001", "name": "Dr. Emily Ross", "score": 110},
        {"provider_id": "P004", "name": "Dr. Michael Lee", "score": 88}
    ],
    "patient_response": "",
    "consent_granted": False
}
```

### After First Decline (State Updated):
```python
{
    "therapist_id": "T001",
    "current_provider_index": 1,  # ← Incremented
    "offers_sent": 1,  # ← Incremented
    "ranked_providers": [
        {"provider_id": "P001", "name": "Dr. Emily Ross", "score": 110},
        {"provider_id": "P004", "name": "Dr. Michael Lee", "score": 88}
    ],
    "patient_response": "NO",  # ← Updated
    "consent_granted": False
}
```

### After Second Accept (Final State):
```python
{
    "therapist_id": "T001",
    "current_provider_index": 1,
    "offers_sent": 2,  # ← 2 offers sent total
    "ranked_providers": [...],
    "patient_response": "YES",  # ← Updated
    "consent_granted": True,  # ← Updated
    "booking_result": {
        "status": "SUCCESS",
        "confirmation_number": "CONF-AUTO",
        "provider_id": "P004"  # ← Dr. Lee (second provider)
    }
}
```

---

## Benefits of LangGraph vs Simple Workflow

| Feature | Simple Workflow | LangGraph Workflow |
|---------|----------------|-------------------|
| **Patient says NO** | ❌ Workflow ends | ✅ Automatically tries next provider |
| **No candidates** | ❌ Workflow fails | ✅ Escalates to HOD automatically |
| **Patient timeout** | ❌ Gets stuck | ✅ Routes to manual review |
| **Retry logic** | ❌ Manual coding | ✅ Built into graph |
| **State tracking** | ⚠️ Manual variables | ✅ Managed by LangGraph |
| **Visual debugging** | ❌ Print statements | ✅ LangSmith UI (see graph execution) |
| **Error recovery** | ❌ Try/catch blocks | ✅ Automatic retry with state persistence |
| **Parallel processing** | ❌ Not supported | ✅ Can process multiple appointments |

---

## Code Comparison

### Simple Workflow (No Branching):
```python
# Always goes in order, no conditions
result = trigger_handler(therapist_id)
filtered = filter_candidates(...)
scored = score_providers(...)
consent = send_offer(...)
booked = book_appointment(...)
audit = create_audit_log(...)
# Can't handle: What if patient says NO?
```

### LangGraph Workflow (With Branching):
```python
# Builds a graph with conditional edges
workflow.add_conditional_edges(
    "consent",
    route_consent,  # Decides where to go next
    {
        "book": "book",           # If YES
        "next_provider": "score",  # If NO (loop back)
        "manual_review": END       # If timeout
    }
)
```

---

## How to Use Both

### In Your Code:
```python
from orchestrator import create_workflow_orchestrator

# Use LangGraph (with branching)
orchestrator = create_workflow_orchestrator(engine="langgraph")

# Or use Simple (sequential only)
orchestrator = create_workflow_orchestrator(engine="simple")

# Same API for both!
result = orchestrator.process_therapist_departure("T001")
```

### Current Demo:
✅ **LangGraph is now the default** (shows branching capabilities)
✅ **Simple is still available** (fallback for simplicity)
✅ **Same UI works with both** (abstracted interface)

---

## Demo Command

Try it now:
```bash
# Run with LangGraph
make dev

# Type in UI:
therapist departed T001

# Watch the conditional branching in action!
```

---

**The workflow now automatically handles:**
✅ Patient declines → Try next provider
✅ No candidates → Escalate to HOD
✅ Patient timeout → Manual review
✅ Multiple appointments → Process sequentially with state

**This is the power of LangGraph! 🚀**

