# Prompt Architecture Validation

> **Date:** 2025-11-20  
> **Goal:** Validate completeness, correctness, and simplicity

---

## 🔍 Current Prompt Inventory

| Prompt Name | Purpose | Used Where? | Priority |
|-------------|---------|-------------|----------|
| `healthcare-chat-router-v1` | Parse user messages | Chat UI entry | ✅ CRITICAL |
| `healthcare-intent-classifier-v1` | Classify intent only | Alternative to router | ⚠️ REDUNDANT |
| `healthcare-entity-extractor-v1` | Extract entities only | Alternative to router | ⚠️ REDUNDANT |
| `provider-scoring-prompt-v1` | Score/rank providers | Smart Scheduling Agent | ✅ CRITICAL |
| `patient-engagement-message-v1` | Generate patient messages | Patient Engagement Agent | ✅ CRITICAL |

---

## 📊 System Flow Analysis

### 1. Chat Entry Point (User → System)

**Current:**
```
User types: "therapist departed T001"
   ↓
[Pattern matching - hardcoded]
   ↓
Extract provider ID
   ↓
Trigger workflow
```

**With LLM:**
```
User types: "Sarah called in sick" / "T001 unavailable" / "therapist departed T001"
   ↓
[LLM: chat-router] ✅
   ↓
Structured JSON: {intent, entities, action}
   ↓
Trigger workflow
```

**Prompt Needed:** ✅ `chat-router` (HAVE IT)

---

### 2. Provider Filtering (Compliance Check)

**Current:**
```python
def filter_candidates(patient_id, appointment_id, candidate_ids):
    # Simple logic: check specialty, status
    # Uses knowledge base for rules
```

**Question:** Do we need LLM here?

**Analysis:**
- Simple rules (specialty match, active status) → No LLM needed
- Complex rules (Medicare POC validation, payer rules) → Could use LLM

**Recommendation:** 
- Start WITHOUT LLM (current logic is fine)
- Add `compliance-checker-v1` prompt ONLY if rules become too complex

**Prompt Needed:** ❌ NOT CRITICAL (future enhancement)

---

### 3. Provider Scoring (Smart Matching)

**Current:**
```python
def score_and_rank_providers(patient_id, appointment_id, qualified_provider_ids):
    # Multi-factor scoring:
    # - Continuity, specialty, location, capacity, preferences
```

**With LLM:**
```
Factors: continuity, specialty, location, capacity, preferences
   ↓
[LLM: provider-scoring] ✅
   ↓
Scored & ranked providers with reasoning
```

**Prompt Needed:** ✅ `provider-scoring` (HAVE IT)

---

### 4. Patient Communication

**Current:**
```python
def send_offer(patient_id, appointment_id, new_provider_id, date, time):
    # Template-based message
    message = f"Hi {patient_name}, Dr. {provider_name} is available..."
```

**With LLM:**
```
Context: patient, provider, appointment
   ↓
[LLM: patient-message] ✅
   ↓
Personalized, empathetic message
```

**Prompt Needed:** ✅ `patient-message` (HAVE IT)

---

### 5. Patient Response Parsing

**Current:**
```python
# URL-based: /patient-response?token=xxx&response=yes
# Simple: "yes" or "no"
```

**Question:** Do we need LLM?

**Analysis:**
- Simple responses ("yes", "no") → Regex is fine
- Complex responses ("can I get more info?", "what time?") → LLM helpful

**Recommendation:**
- Start WITHOUT LLM (current URL-based is fine)
- Add `patient-response-parser-v1` if we add conversational replies

**Prompt Needed:** ❌ NOT CRITICAL (future enhancement)

---

### 6. Query Handling (Receptionist Questions)

**Examples:**
- "show waitlist"
- "what's Maria's appointment status?"
- "who's on call today?"

**Current:** Not implemented

**With LLM:**
```
User: "show waitlist"
   ↓
[LLM: query-handler] ❌ MISSING
   ↓
{intent: "QUERY_WAITLIST", action: "get_waitlist"}
```

**Prompt Needed:** ⚠️ `query-handler-v1` (MISSING - but covered by chat-router)

---

## 🎯 Architecture Assessment

### ❌ ISSUE 1: Redundancy

We have **3 prompts** that do similar things:

1. **chat-router** - Does intent + entity extraction together
2. **intent-classifier** - Just intent
3. **entity-extractor** - Just entities

**Problem:** This is redundant and confusing.

**Options:**

#### Option A: Use Only Chat Router (RECOMMENDED)
```
User message → [chat-router] → {intent, entities, action}
```
✅ Simple, one LLM call
✅ Fastest
✅ Easiest to maintain

#### Option B: Use Pipeline
```
User message → [intent-classifier] → [entity-extractor] → {intent, entities}
```
❌ Two LLM calls (slower, more expensive)
✅ More modular (can optimize each separately)

#### Option C: Hybrid
```
User message → [chat-router] (fast path)
If ambiguous → [entity-extractor] (clarification)
```
✅ Best of both worlds
⚠️ More complex

**RECOMMENDATION:** Go with **Option A** (chat-router only)
- Simpler architecture
- Faster (1 LLM call vs 2)
- Cheaper
- Add specialized prompts ONLY when needed

---

### ❌ ISSUE 2: Missing Prompts

Based on system flow, we're missing:

1. **Clarification Generator** (When ambiguous)
   ```
   User: "Sarah is sick"
   System: "I found Dr. Sarah Johnson (T001) and Sarah Miller (PAT004). Which?"
   ```
   
2. **Query Response** (Already covered by chat-router!)
   ```
   User: "show waitlist"
   [chat-router detects QUERY_WAITLIST intent]
   ```

**RECOMMENDATION:** 
- Add `clarification-generator-v1` for ambiguity handling
- Query handling already covered by chat-router ✅

---

## ✅ REVISED PROMPT ARCHITECTURE (SIMPLIFIED)

### Core Prompts (Must Have)

| # | Prompt | Purpose | When Used |
|---|--------|---------|-----------|
| 1 | `healthcare-chat-router-v1` | Parse all user messages | Every chat message |
| 2 | `provider-scoring-prompt-v1` | Score/rank providers | Provider matching |
| 3 | `patient-engagement-message-v1` | Generate patient messages | Patient communication |

**Total: 3 prompts** (down from 5) ✅

---

### Optional Prompts (Add When Needed)

| # | Prompt | Purpose | Priority |
|---|--------|---------|----------|
| 4 | `clarification-generator-v1` | Handle ambiguity | LOW (add later) |
| 5 | `compliance-checker-v1` | Complex rule interpretation | LOW (current logic is fine) |
| 6 | `patient-response-parser-v1` | Parse conversational replies | LOW (URL-based works) |

---

## 🏗️ SIMPLIFIED ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│  CHAT UI                                                │
│  "Sarah is sick" / "therapist departed T001"           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ↓
         [LLM: chat-router] ← SINGLE ENTRY POINT
                  │
                  ↓
         {intent, entities, action}
                  │
         ┌────────┴────────┬────────────────┐
         ↓                 ↓                ↓
   THERAPIST_         QUERY_          PATIENT_
   UNAVAILABLE        STATUS          DECLINED
         │                 │                │
         ↓                 ↓                ↓
   Trigger            Get Data        Backfill
   Workflow          Return JSON      Workflow
         │
         ↓
   ┌─────────────────────────────────────────┐
   │  Smart Scheduling Agent                 │
   │  1. Filter (no LLM - simple logic)      │
   │  2. Score [LLM: provider-scoring] ✅    │
   │  3. Rank                                │
   └─────────────┬───────────────────────────┘
                 │
                 ↓
   ┌─────────────────────────────────────────┐
   │  Patient Engagement Agent               │
   │  [LLM: patient-message] ✅              │
   │  Generate personalized message          │
   └─────────────────────────────────────────┘
```

**LLM Calls: 3 per workflow**
1. Chat router (parse user input)
2. Provider scoring (rank providers)
3. Patient message (generate message)

---

## ✅ VALIDATION RESULTS

### Completeness: ✅ PASS
- All critical LLM calls have prompts
- Query handling covered by chat-router
- Patient response parsing not needed (URL-based)

### Architecture: ⚠️ NEEDS SIMPLIFICATION
- **Remove:** `intent-classifier` and `entity-extractor` (redundant)
- **Keep:** `chat-router`, `provider-scoring`, `patient-message`
- **Add Later:** `clarification-generator` when needed

### Simplicity: ✅ PASS (After Cleanup)
- 3 core prompts (down from 5)
- Clear separation of concerns:
  - `chat-router` → Parse user input
  - `provider-scoring` → Rank providers
  - `patient-message` → Generate messages
- Easy to understand and maintain

---

## 🎯 RECOMMENDATIONS

### Immediate Actions

1. **Remove Redundant Prompts**
   ```yaml
   # DELETE from prompts/langfuse_prompts.yaml
   - healthcare-intent-classifier-v1  ❌
   - healthcare-entity-extractor-v1   ❌
   ```

2. **Keep Core Prompts**
   ```yaml
   # KEEP these 3
   - healthcare-chat-router-v1        ✅
   - provider-scoring-prompt-v1       ✅
   - patient-engagement-message-v1    ✅
   ```

3. **Update .env**
   ```bash
   # Remove
   LANGFUSE_PROMPT_INTENT_CLASSIFIER=...  ❌
   LANGFUSE_PROMPT_ENTITY_EXTRACTOR=...   ❌
   
   # Keep
   LANGFUSE_PROMPT_CHAT_ROUTER=healthcare-chat-router-v1  ✅
   LANGFUSE_PROMPT_PROVIDER_SCORER=provider-scoring-prompt-v1  ✅
   LANGFUSE_PROMPT_PATIENT_MESSAGE=patient-engagement-message-v1  ✅
   ```

### Future Enhancements (When Needed)

4. **Add Clarification Prompt** (if users are confused)
   ```yaml
   clarification-generator-v1:
     purpose: Handle ambiguous inputs
     example: "Did you mean Dr. Sarah or Sarah Miller?"
   ```

5. **Add Compliance Checker** (if rules get complex)
   ```yaml
   compliance-checker-v1:
     purpose: Interpret complex payer/POC rules
     example: "Can this provider treat Medicare patients?"
   ```

---

## 📊 Cost Comparison

### Current (5 prompts):
```
Per workflow:
- chat-router: 1 call
- intent-classifier: 1 call (redundant!)
- entity-extractor: 1 call (redundant!)
- provider-scoring: 1 call
- patient-message: 1 call

Total: 5 LLM calls per workflow
Cost: ~$0.05 per workflow
```

### Simplified (3 prompts):
```
Per workflow:
- chat-router: 1 call
- provider-scoring: 1 call
- patient-message: 1 call

Total: 3 LLM calls per workflow
Cost: ~$0.03 per workflow

Savings: 40% cheaper! 💰
```

---

## ✅ FINAL VERDICT

**Architecture:** ✅ Correct (after removing redundancy)  
**Completeness:** ✅ All critical paths covered  
**Simplicity:** ✅ 3 prompts is the sweet spot

**Action Required:** Remove 2 redundant prompts (intent-classifier, entity-extractor)

**Result:** Clean, simple, cost-effective architecture! 🎉

