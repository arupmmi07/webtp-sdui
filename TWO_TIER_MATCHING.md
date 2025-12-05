# 🎯 Two-Tier Matching Approach

## Overview

The orchestrator now uses a **two-tier matching approach** to ensure critical requirements are met before considering preferences.

---

## 📊 Tier Structure

### **TIER 1 - Exact Match (MUST HAVE - Hard Requirements)**

These are **CRITICAL** requirements that **MUST** be met. If no provider meets ALL Tier 1 requirements, the patient **MUST** be assigned to waitlist/HOD review.

#### Requirements:

1. **Specialty Match (CRITICAL)**
   - If patient requires a specific specialty (e.g., "orthopedic", "sports medicine"), provider MUST have that specialty
   - Example: Patient with "post-surgical knee" requires "orthopedic" specialty
   - If NO provider has the required specialty → **WAITLIST**
   - If patient condition is general (no specific specialty required), any provider can be considered

2. **Provider Availability (CRITICAL)**
   - Provider MUST have available slots on appointment date
   - Provider MUST not be at maximum capacity (`current_patient_load < max_patient_capacity`)

3. **Basic Feasibility (CRITICAL)**
   - Provider MUST be active
   - Provider location MUST be within patient's `max_distance_miles` (if specified)

---

### **TIER 2 - Preference Match (NICE TO HAVE - Soft Requirements)**

These are preferences used to **RANK and SELECT** the best provider from those that meet Tier 1 requirements.

#### Preferences:

1. **Gender Preference**
   - Patient's gender preference (if specified)
   - If "any" or not specified, not a requirement

2. **Day Preference**
   - Patient's preferred days of the week
   - Earlier time slots preferred

3. **Location/Proximity**
   - Same zip code preferred
   - Closer locations preferred

4. **Continuity of Care**
   - Prior provider relationships
   - Same provider on different day (continuity slots)

5. **Experience Level**
   - Provider experience matching patient needs
   - Years of experience

6. **Load Balancing**
   - Prefer providers with lower current patient load
   - Distribute appointments evenly

---

## 🔄 Matching Logic

### **STEP 1 - Tier 1 Filtering**

For each patient:

1. Check if patient requires a specific specialty (`condition_specialty_required`)
2. Filter providers to ONLY those that:
   - ✅ Have the required specialty (or can handle the condition)
   - ✅ Have available slots
   - ✅ Are within capacity limits
   - ✅ Are within distance limits (if `max_distance_miles` specified)
3. **If NO providers pass Tier 1** → assign to waitlist with `action: "waitlist"`
4. **If providers pass Tier 1** → proceed to Tier 2 ranking

### **STEP 2 - Tier 2 Ranking**

From providers that passed Tier 1:

1. Rank providers based on Tier 2 preferences
2. Select the best match considering:
   - Gender preference match
   - Day preference match
   - Location proximity
   - Continuity of care
   - Experience level
   - Load balancing
3. Assign to the highest-ranked provider

---

## 📋 Decision Quality

- **EXCELLENT**: All Tier 1 requirements met + Most Tier 2 preferences met
- **GOOD**: All Tier 1 requirements met + Some Tier 2 preferences met
- **ACCEPTABLE**: All Tier 1 requirements met + Few Tier 2 preferences met
- **POOR**: Tier 1 requirements NOT met → **MUST assign to waitlist**

---

## 💡 Examples

### Example 1: Tier 1 Pass → Tier 2 Ranking

**Patient:** Maria Rodriguez
- Condition: "post-surgical knee"
- Required Specialty: "orthopedic"
- Gender Preference: "female"
- Preferred Days: "Tuesday,Thursday"

**Available Providers:**
- Dr. Emily Ross: Sports Physical Therapy ❌ (Tier 1 FAIL - wrong specialty)
- Dr. Anna Martinez: Orthopedic Physical Therapy ✅ (Tier 1 PASS)
- Dr. Michael Lee: Geriatric Physical Therapy ❌ (Tier 1 FAIL - wrong specialty)

**Result:**
- Tier 1: Only Dr. Anna Martinez passes (has orthopedic specialty)
- Tier 2: Dr. Anna Martinez matches gender preference (female) ✅
- **Assignment:** Dr. Anna Martinez (EXCELLENT match)

---

### Example 2: Tier 1 Fail → Waitlist

**Patient:** John Davis
- Condition: "Complex post-surgical shoulder rehabilitation"
- Required Specialty: "Orthopedic Physical Therapy with Post-Surgical Specialization"
- Preferred Days: "Saturday,Sunday"

**Available Providers:**
- Dr. Emily Ross: Sports Physical Therapy ❌
- Dr. James Wilson: Acupuncture & Manual Therapy ❌
- Dr. Michael Lee: Geriatric Physical Therapy ❌
- (All providers have different specialties, none match required specialty)

**Result:**
- Tier 1: **NO providers pass** (none have required specialty)
- **Action:** Waitlist (POOR match, Tier 1 requirements not met)

---

### Example 3: Tier 1 Pass → Multiple Tier 2 Options

**Patient:** Susan Lee
- Condition: "hip replacement recovery"
- Required Specialty: "orthopedic"
- Gender Preference: "female"
- Preferred Days: "Tuesday,Thursday"

**Available Providers (all pass Tier 1):**
- Dr. Anna Martinez: Orthopedic PT, Female ✅✅
- Dr. Emily Ross: Sports PT (can handle orthopedic), Female ✅✅
- Dr. Michael Lee: Geriatric PT (can handle orthopedic), Male ✅

**Result:**
- Tier 1: All 3 providers pass (all can handle orthopedic)
- Tier 2 Ranking:
  1. Dr. Anna Martinez (exact specialty match + gender match + day match)
  2. Dr. Emily Ross (can handle + gender match + day match)
  3. Dr. Michael Lee (can handle, but gender mismatch)
- **Assignment:** Dr. Anna Martinez (EXCELLENT match)

---

## 🚨 Important Rules

1. **NEVER assign a patient if Tier 1 requirements are not met** - always waitlist
2. **Specialty mismatch (when specialty is required) is a Tier 1 blocker** - do not assign
3. **If patient has restrictive requirements** (e.g., weekend-only, very specific specialty) and no provider matches, **waitlist immediately**
4. **Use Tier 2 preferences only to rank** among providers that meet Tier 1 requirements
5. **Provide clear reasoning** explaining Tier 1 pass/fail and Tier 2 ranking

---

## 📝 Output Format

The LLM response includes reasoning that clearly states Tier 1 and Tier 2 evaluation:

```json
{
  "reasoning": "Tier 1: ✅ Specialty match (orthopedic required, provider has orthopedic specialty), ✅ Available slots, ✅ Within capacity. Tier 2: ✅ Gender preference met (female), ✅ Same zip code, ✅ Day preference met (Thursday), ✅ Continuity with prior provider. Excellent overall match.",
  "match_factors": {
    "tier1_specialty_match": true,
    "tier1_availability": true,
    "tier1_capacity": true,
    "tier2_gender_preference_met": true,
    "tier2_location_match": true,
    "tier2_day_preference_met": true,
    "tier2_continuity": true
  },
  "match_quality": "EXCELLENT",
  "action": "assign"
}
```

---

## ✅ Benefits

1. **Ensures Critical Requirements**: Patients with specific specialty needs are never mismatched
2. **Prevents Bad Assignments**: Specialty mismatches automatically go to waitlist
3. **Optimizes Preferences**: Among valid providers, selects the best match
4. **Clear Decision Logic**: Two-step process is easy to understand and audit
5. **Better Patient Care**: Ensures patients get appropriate specialty care

---

**Status**: ✅ **Two-Tier Matching Implemented**

