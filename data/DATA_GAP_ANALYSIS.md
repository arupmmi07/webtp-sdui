# Data Gap Analysis: USE_CASES.md vs Current Data

## Executive Summary

❌ **CRITICAL GAPS FOUND** - Current data supports basic demo but missing ~60% of fields required for full use case implementation.

**Current State:**
- ✅ 3 patients (need 15+ for realistic demo)
- ✅ 4 providers (need 8+ per use cases)
- ✅ 3 appointments (need 15+ per use cases)
- ❌ Missing critical fields for priority scoring, compliance, and backfill

---

## Use Case 1: Trigger - Identify Affected Appointments with Priority

### USE_CASES.md Requirements:
```
- 15 scheduled appointments for Dr. Sarah Johnson
- Priority calculation needs:
  * no_show_risk (0-1 scale)
  * POC expiration dates
  * revenue_value (normalized 0-1)
  * patient_satisfaction_risk (0-1)
```

### Current Data Reality:
| Field | Required | Current | Status |
|-------|----------|---------|--------|
| Appointments for T001 | 15 | 3 | ❌ Missing 12 |
| `no_show_risk` | Yes | ❌ Not present | ❌ MISSING |
| `poc_expiration_date` | Yes | ❌ Not present | ❌ MISSING |
| `revenue_value` | Yes | ❌ Not present | ❌ MISSING |
| `patient_satisfaction_risk` | Yes | ❌ Not present | ❌ MISSING |
| `insurance_type` | Yes | ❌ Not present | ❌ MISSING |
| `clinical_urgency` | Yes | ❌ Not present | ❌ MISSING |

### Impact:
- ⚠️ **Cannot calculate priority scores** as described in UC1
- ⚠️ **Cannot demonstrate realistic appointment volume** (3 vs 15)
- ⚠️ **Cannot show high/medium/low priority buckets**

### Recommendation:
**ADD TO `patients.json`:**
```json
{
  "patient_id": "PAT001",
  "no_show_risk": 0.8,
  "no_show_history": {"last_12_months": 3, "total_appointments": 8},
  "poc_expiration_date": "2024-12-15",
  "insurance_type": "Medicare",
  "revenue_value": 120.0,
  "patient_satisfaction_risk": 0.2,
  "clinical_urgency": "medium",
  "vip_status": false
}
```

**ADD TO `appointments.json`:**
- Add 12 more appointments (A004-A015) for realistic demo

---

## Use Case 2: Match Candidate Filtering with Compliance

### USE_CASES.md Requirements:
```
- 8 available therapists to filter
- 8 compliance filters:
  1. Required Skills/Certifications
  2. License & Privileges
  3. POC Status Validation
  4. Payer Rules Compliance
  5. Location Constraint
  6. Telehealth Flag
  7. Availability Check
  8. Capacity Check
```

### Current Data Reality:
| Field | Required | Current | Status |
|-------|----------|---------|--------|
| Number of providers | 8 | 4 | ❌ Missing 4 |
| `certifications` | Yes | ❌ Not present | ❌ MISSING |
| `license_status` | Yes | ❌ Not present | ❌ MISSING |
| `hospital_privileges` | Yes | ❌ Not present | ❌ MISSING |
| `medicare_approved` | Yes | ❌ Not present | ❌ MISSING |
| `npi_number` | Yes | ❌ Not present | ❌ MISSING |
| `poc_approved_provider` | Yes | ❌ Not present | ❌ MISSING |
| `telehealth_available` | Yes | ❌ Not present | ❌ MISSING |
| `availability_slots` | Yes | ❌ Not present | ❌ MISSING |
| `location_address` | Yes | ❌ Partial (distance only) | ⚠️ INCOMPLETE |

### Impact:
- ⚠️ **Cannot demonstrate 8 compliance filters** (currently can only demo ~3)
- ⚠️ **Cannot show POC validation** (critical for Medicare)
- ⚠️ **Cannot show telehealth vs in-person filtering**

### Recommendation:
**ADD TO `providers.json`:**
```json
{
  "provider_id": "P001",
  "certifications": ["Orthopedic PT", "Manual Therapy", "Dry Needling"],
  "license_status": "active",
  "license_number": "PT12345-CA",
  "hospital_privileges": true,
  "medicare_approved": true,
  "npi_number": "1234567890",
  "poc_approved_provider": true,
  "telehealth_available": false,
  "in_person_available": true,
  "availability_slots": [
    {"day": "Tuesday", "time": "10:00 AM", "available": true},
    {"day": "Tuesday", "time": "2:00 PM", "available": false}
  ],
  "location_address": "123 Main St, Metro City, CA 90001"
}
```

**ADD 4 MORE PROVIDERS** (P005-P008):
- P005: Pediatric specialist (to show skills filter elimination)
- P006: Sports Medicine + Orthopedic (like UC describes)
- P007: Far location (to show distance filter)
- P008: Fully booked (to show availability filter)

---

## Use Case 3: Compliance and Score Gating

### USE_CASES.md Requirements:
```
Scoring Factors (Total: 150 points):
- Continuity Score: 40 points (prior provider relationship)
- Specialty Match: 35 points (exact specialty vs. general)
- Patient Preference Fit: 30 points (gender, age, language, etc.)
- Schedule Load Balance: 25 points (lower load = higher score)
- Day/Time Match: 20 points (matches patient's preferred day/time)
```

### Current Data Reality:
| Scoring Factor | Required Fields | Current | Status |
|----------------|----------------|---------|--------|
| Continuity | `prior_providers` | ✅ Present | ✅ OK |
| Specialty Match | `specialty`, `certifications` | ⚠️ Partial | ⚠️ INCOMPLETE |
| Patient Preference | `gender`, `age`, `language` | ⚠️ Partial | ⚠️ INCOMPLETE |
| Schedule Load | `current_patient_load`, `max_capacity` | ✅ Present | ✅ OK |
| Day/Time Match | `availability_slots`, `preferred_days` | ⚠️ Partial | ⚠️ INCOMPLETE |

### Missing for Full Scoring:
- Provider `age` (for age similarity scoring)
- Provider `language` preferences
- Provider `years_experience`
- Detailed `specialty_level` (specialist vs general)
- Patient `language` preference
- Actual `availability_slots` for providers

### Recommendation:
**ADD TO `providers.json`:**
```json
{
  "age": 48,
  "years_experience": 12,
  "languages": ["English", "Spanish"],
  "specialty_level": "specialist",
  "patient_rating": 4.9,
  "total_reviews": 128
}
```

**ADD TO `patients.json`:**
```json
{
  "language_preference": "English",
  "preferred_provider_gender": "female"
}
```

---

## Use Case 4: Automated Patient Offer Flow with Multi-Channel

### USE_CASES.md Requirements:
```
- Communication preference: SMS (primary), Email (backup)
- Timeout: 24 hours
- Multiple response scenarios: YES/NO/INFO/TIMEOUT
```

### Current Data Reality:
| Field | Required | Current | Status |
|-------|----------|---------|--------|
| `communication_channel_primary` | "SMS" | "email" | ⚠️ WRONG VALUE |
| `communication_channel_backup` | Yes | ❌ Not present | ❌ MISSING |
| `consent_timeout_hours` | Yes | ❌ Not present | ❌ MISSING |
| `phone` (for SMS) | Yes | ✅ Present | ✅ OK |
| `email` (for backup) | Yes | ✅ Present | ✅ OK |

### Recommendation:
**UPDATE `patients.json`:**
```json
{
  "communication_channel_primary": "sms",
  "communication_channel_backup": "email",
  "consent_timeout_hours": 24,
  "reminder_timeout_hours": 12
}
```

---

## Use Case 5: Waitlist & Backfill Automation with High No-Show Targeting

### USE_CASES.md Requirements:
```
- John Davis: High no-show risk (0.9), workers comp, flexible schedule
- High no-show risk patient list (>=0.6)
- HOD (Head of Department) for fallback
- Availability windows
```

### Current Data Reality:
| Field | Required | Current | Status |
|-------|----------|---------|--------|
| `no_show_risk` | 0.9 for John | ❌ Not present | ❌ MISSING |
| `insurance_type` | "workers_comp" | ❌ Not present | ❌ MISSING |
| `availability_windows` | Yes | ❌ Not present | ❌ MISSING |
| `flexibility` | "high" | ❌ Not present | ❌ MISSING |
| HOD provider | Yes | ❌ Not designated | ❌ MISSING |
| Waitlist patients | Yes | ❌ No data | ❌ MISSING |

### Impact:
- ⚠️ **Cannot demonstrate high no-show targeting** (core feature of UC5)
- ⚠️ **Cannot show HOD fallback** (important safety net)
- ⚠️ **Cannot show availability window matching**

### Recommendation:
**UPDATE `patients.json` for PAT002 (John Davis):**
```json
{
  "patient_id": "PAT002",
  "no_show_risk": 0.9,
  "no_show_history": {"last_12_months": 7, "total_appointments": 10},
  "insurance_type": "workers_comp",
  "flexibility": "high",
  "availability_windows": [
    {"days": ["Monday", "Wednesday", "Friday"], "times": ["7-11 AM", "4-6 PM"]},
    {"cannot_do": ["Tuesday"]}
  ]
}
```

**ADD HOD TO `providers.json`:**
```json
{
  "provider_id": "P999",
  "name": "Dr. Robert Williams",
  "specialty": "general",
  "role": "HOD",
  "is_fallback_provider": true,
  "status": "active"
}
```

**ADD WAITLIST PATIENTS:**
- Need 3-5 high no-show risk patients for backfill demo

---

## Use Case 6: Final Appointment Reconciliation & Audit

### USE_CASES.md Requirements:
```
- Comprehensive audit log (JSON format)
- Session tracking
- Revenue impact calculation
- Stakeholder notifications
- Compliance verification
```

### Current Data Reality:
| Field | Required | Current | Status |
|-------|----------|---------|--------|
| `session_id` | Yes | ❌ Runtime only | ⚠️ PARTIAL |
| `revenue_value` per appointment | Yes | ❌ Not present | ❌ MISSING |
| Audit log format | Yes | ✅ Generated | ✅ OK |
| Event tracking | Yes | ✅ Implemented | ✅ OK |

### Recommendation:
**ADD TO `appointments.json`:**
```json
{
  "revenue_value": 120.0,
  "billing_code": "97110",
  "authorization_number": "AUTH-12345"
}
```

---

## Overall Data Completeness

| Category | Completeness | Critical Gaps |
|----------|--------------|---------------|
| **Basic Patient Info** | 80% | Missing no-show risk, insurance, POC dates |
| **Basic Provider Info** | 70% | Missing certifications, license details, availability |
| **Appointments** | 50% | Only 3 vs 15 needed, missing revenue values |
| **Compliance Data** | 30% | Missing POC validation, payer rules, licenses |
| **Scoring Data** | 60% | Missing age, languages, detailed specialties |
| **Backfill Data** | 20% | Missing no-show risk, waitlist, HOD, availability |

**OVERALL: 52% Complete** ❌

---

## Priority Recommendations

### 🔴 CRITICAL (Must Have for Demo):
1. **Add no-show risk to all patients** (needed for UC1 and UC5)
2. **Add insurance type to all patients** (Medicare, Workers Comp, etc.)
3. **Add POC expiration dates** (critical for compliance filtering)
4. **Add 4 more providers** (P005-P008) to reach 8 total
5. **Add 12 more appointments** (A004-A015) for realistic volume
6. **Designate HOD provider** (fallback for UC5)

### 🟡 IMPORTANT (Enhances Demo):
7. **Add provider certifications and licenses**
8. **Add telehealth availability flags**
9. **Add provider availability slots**
10. **Add patient availability windows**
11. **Change communication_channel_primary to "sms"**
12. **Add 3-5 waitlist patients with high no-show risk**

### 🟢 NICE TO HAVE (Completeness):
13. **Add provider age, language, years_experience**
14. **Add patient language preference**
15. **Add revenue values per appointment**
16. **Add detailed location addresses**
17. **Add patient VIP status and satisfaction history**

---

## Quick Fix Summary

**Minimum to make USE_CASES.md work:**

1. **Expand `patients.json`** to 15 patients with:
   - no_show_risk, insurance_type, poc_expiration_date
   
2. **Expand `providers.json`** to 8 providers with:
   - certifications, medicare_approved, telehealth_available
   
3. **Expand `appointments.json`** to 15 appointments with:
   - All 15 assigned to T001 initially
   - revenue_value field added

4. **Add special providers:**
   - HOD (Dr. Robert Williams)
   - Different specialties for filter demo

5. **Update existing data:**
   - Change PAT001 communication to "sms"
   - Add John Davis no-show risk 0.9
   - Add Maria Rodriguez Medicare insurance

**Estimated effort:** 2-3 hours to add all data properly.

---

## Sample Enhanced Patient Record

```json
{
  "patient_id": "PAT001",
  "name": "Maria Rodriguez",
  "age": 50,
  "gender": "female",
  "phone": "+1-555-234-5678",
  "email": "maria.r@email.com",
  "language_preference": "English",
  "condition": "post-surgical knee",
  "condition_specialty_required": "orthopedic",
  "clinical_urgency": "medium",
  "gender_preference": "female",
  "preferred_days": "Tuesday,Thursday",
  "preferred_time_block": "morning",
  "max_distance_miles": 10.0,
  "communication_channel_primary": "sms",
  "communication_channel_backup": "email",
  "prior_providers": [],
  
  "insurance_type": "Medicare",
  "poc_status": "active",
  "poc_expiration_date": "2024-12-15",
  "poc_approved_providers": ["T001", "P001", "P004", "P006"],
  
  "no_show_risk": 0.8,
  "no_show_history": {
    "last_12_months": 3,
    "total_appointments": 8,
    "last_no_show_date": "2024-08-15"
  },
  
  "revenue_value_per_visit": 120.0,
  "patient_satisfaction_risk": 0.2,
  "vip_status": false,
  "complaints_history": 0,
  
  "availability_windows": [
    {"days": ["Tuesday", "Thursday"], "times": ["9 AM - 12 PM"]},
    {"cannot_do": ["Wednesday"]}
  ]
}
```

Would you like me to generate the complete enhanced data files with all these fields?

