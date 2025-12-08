# Use Case Coverage Analysis

## 📊 Current Support Status

### ✅ 1. Gender Preference - **FULLY SUPPORTED**
**Requirement:** If patient is a woman → prefer a female provider on the same day or closest available date.

**Current Implementation:**
- ✅ Patient has `gender_preference` field (e.g., "female", "male", "any")
- ✅ Provider has `gender` field
- ✅ Scoring: +15 points for gender match
- ✅ Visible in UI tooltips

**Files:**
- `data/patients.json`: `"gender_preference": "female"`
- `agents/smart_scheduling_agent.py`: Line 288-289, 324
- `static/schedule.html`: Gender preference shown in tooltips

**Demo Ready:** ✅ YES

---

### ⚠️ 2. Current Provider Availability - **PARTIALLY SUPPORTED**
**Requirement:** If the patient's current provider has an earlier slot than others → assign that provider.

**Current Implementation:**
- ✅ Provider has `available_days` field
- ✅ Provider has `working_hours_start` and `working_hours_end`
- ✅ Provider has `unavailable_dates` field
- ⚠️ **MISSING:** Time slot comparison logic (earliest slot wins)
- ⚠️ **MISSING:** Explicit bonus for "same provider, earlier slot"

**Gap:**
- System filters by availability but doesn't explicitly prioritize earlier time slots
- System doesn't give bonus points for "earlier availability"

**Enhancement Needed:** 
- Add time slot scoring: earlier slots get higher scores
- Track available time slots per provider, not just days

**Demo Ready:** ⚠️ PARTIAL - availability checked, but not "earliest slot" priority

---

### ✅ 3. Previous Consultations - **FULLY SUPPORTED**
**Requirement:** If there is a provider the patient has seen before → prioritize that provider.

**Current Implementation:**
- ✅ Patient has `prior_providers` field (array of provider IDs)
- ✅ Scoring: +25 points for continuity bonus (line 325)
- ✅ Scoring breakdown shows "continuity" score (line 362)
- ✅ LLM prompt includes prior providers (line 308)

**Files:**
- `data/patients.json`: `"prior_providers": ["T001"]`
- `agents/smart_scheduling_agent.py`: Line 308, 325, 362

**Demo Ready:** ✅ YES - Maria Rodriguez has prior_providers: ["T001"]

---

### ❌ 4. Experience Match - **NOT SUPPORTED**
**Requirement:** If assigning a new provider → ensure they have similar experience and expertise to the previous one.

**Current Implementation:**
- ✅ Provider has `certifications` field (shows expertise)
- ❌ **MISSING:** `years_experience` field
- ❌ **MISSING:** `experience_level` field (junior, mid, senior)
- ❌ **MISSING:** Experience comparison logic

**Gap:**
- No way to compare experience levels between providers
- No scoring bonus for matching experience level

**Enhancement Needed:**
- Add `years_experience: int` to provider data
- Add `experience_level: "junior" | "mid-level" | "senior"` to provider data
- Add scoring logic: +20 points if new provider has >= same experience as previous
- Update LLM prompt to consider experience

**Demo Ready:** ❌ NO - data and logic missing

---

### ✅ 5. Patient's Preferred Day - **FULLY SUPPORTED**
**Requirement:** Try to match the patient's preferred appointment day whenever possible.

**Current Implementation:**
- ✅ Patient has `preferred_days` field (e.g., "Tuesday,Thursday")
- ✅ Patient has `preferred_time_block` field (e.g., "morning", "afternoon")
- ✅ Scoring breakdown includes "day_time_match" (line 363)
- ✅ Visible in UI tooltips

**Files:**
- `data/patients.json`: `"preferred_days": "Tuesday,Thursday"`
- `agents/smart_scheduling_agent.py`: Line 363
- `static/schedule.html`: Day preference shown in tooltips

**Demo Ready:** ✅ YES

---

### ✅ 6. Fallback Rule - **FULLY SUPPORTED**
**Requirement:** If no provider matches any of the above → assign the HOD by default, even if they don't have an available slot.

**Current Implementation:**
- ✅ HOD (Head of Department) logic implemented
- ✅ Patients assigned to HOD when no suitable providers found
- ✅ UI shows "⚠️ NEEDS REVIEW" for HOD assignments (yellow)
- ✅ Audit log tracks HOD assignments

**Files:**
- `workflows/langgraph_workflow.py`: HOD fallback in workflow
- `static/schedule.html`: Yellow highlighting for needs_review

**Demo Ready:** ✅ YES - Robert Chen gets assigned to HOD

---

## 📈 Summary Table

| # | Use Case                      | Status           | Score Impact | Demo Ready | Enhancement Needed |
|---|-------------------------------|------------------|--------------|------------|-------------------|
| 1 | Gender Preference             | ✅ FULL          | +15 pts      | ✅ YES     | None              |
| 2 | Current Provider Availability | ⚠️ PARTIAL       | Not scored   | ⚠️ PARTIAL | Time slot scoring |
| 3 | Previous Consultations        | ✅ FULL          | +25 pts      | ✅ YES     | None              |
| 4 | Experience Match              | ❌ NOT SUPPORTED | 0 pts        | ❌ NO      | Add experience data + logic |
| 5 | Patient's Preferred Day       | ✅ FULL          | +10 pts      | ✅ YES     | None              |
| 6 | Fallback Rule (HOD)           | ✅ FULL          | N/A          | ✅ YES     | None              |

**Overall Coverage: 4/6 FULL + 1/6 PARTIAL + 1/6 MISSING = 67% Complete**

---

## 🔧 Required Enhancements

### Priority 1: Add Experience Tracking (Use Case #4)

**1. Update Provider Data Model:**
```json
{
  "provider_id": "T001",
  "name": "Dr. Sarah Johnson",
  "specialty": "Orthopedic Physical Therapy",
  "years_experience": 12,
  "experience_level": "senior",
  "certifications": ["OCS", "Manual Therapy Certified"]
}
```

**2. Update Scoring Logic:**
```python
# Add experience match scoring
if new_provider.years_experience >= original_provider.years_experience:
    score += 20  # Experience match bonus
```

**3. Update LLM Prompt:**
```
EXPERIENCE MATCHING:
- Original provider: {original_provider.years_experience} years, {original_provider.experience_level}
- New provider must have similar or better experience
- Experience match = +20 points
```

---

### Priority 2: Enhance Time Slot Priority (Use Case #2)

**1. Add Time Slot Tracking:**
```json
{
  "provider_id": "P001",
  "available_slots": [
    {"date": "2025-11-21", "time": "09:00", "available": true},
    {"date": "2025-11-21", "time": "10:30", "available": true}
  ]
}
```

**2. Add Time Slot Scoring:**
```python
# Earlier time slots get higher scores
if slot_time < other_provider_slot_time:
    score += 15  # Earlier slot bonus
```

**3. Same Provider Earlier Slot Bonus:**
```python
# If same provider as original, and has earlier slot
if provider_id == original_provider_id and has_earlier_slot:
    score += 30  # Strong continuity + convenience bonus
```

---

## 🎯 Recommended Action Plan

### Option A: Quick Fix (10 minutes)
1. Add `years_experience` to all providers in `data/providers.json`
2. Add experience scoring to `smart_scheduling_agent.py`
3. Update UI tooltips to show experience
4. **Result:** 5/6 fully supported (83%)

### Option B: Complete Implementation (30 minutes)
1. Implement Option A (experience tracking)
2. Add time slot tracking and scoring
3. Update LLM prompts
4. Enhance UI to show time slots
5. **Result:** 6/6 fully supported (100%)

### Option C: Demo Now, Enhance Later
1. Document current 67% coverage
2. Demo with what we have (4 use cases work great!)
3. Mark #2 and #4 as "Phase 2" enhancements
4. **Result:** Clear roadmap, functional demo

---

## 💡 What We Can Demo Today

**Strong Demonstrations:**
1. ✅ Gender preference matching (Maria → female PT)
2. ✅ Prior provider continuity (patients prefer their known PTs)
3. ✅ Preferred day matching (Tuesday/Thursday patients)
4. ✅ HOD fallback (complex cases get manual review)

**Limited Demonstrations:**
5. ⚠️ Availability checking (yes, but not "earliest slot")

**Cannot Demonstrate:**
6. ❌ Experience matching (data doesn't exist yet)

**Demo Script Adjustment:**
"Our system handles 4 of the 6 priority matching rules today:
- Gender preferences ✅
- Provider continuity ✅  
- Day preferences ✅
- HOD fallback ✅

We're adding time slot optimization and experience matching in Phase 2."

---

## 📋 Files to Update (for Full Support)

1. `data/providers.json` - Add years_experience, experience_level
2. `api/server.py` - Update Provider model
3. `agents/smart_scheduling_agent.py` - Add experience scoring (line ~325)
4. `prompts/langfuse_prompts.yaml` - Update provider-scoring-prompt
5. `static/schedule.html` - Add experience to provider tooltips
6. `data/appointments.json` - Add time slots if needed

**Estimated Time:** 20-30 minutes for full implementation
**Risk:** Low - additive changes, no breaking changes

