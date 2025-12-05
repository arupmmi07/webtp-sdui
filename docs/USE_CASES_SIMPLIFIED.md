# Use Cases - Simplified Demo Version

> **📌 Note:** This document matches the **current working demo** (3 appointments, 4 providers).  
> **For the full vision**, see **[USE_CASES.md](USE_CASES.md)** which describes the complete system with 15 appointments, 8 providers, and advanced features.

This document provides detailed mapping of all 6 use cases **optimized for the current demo data**.

**Demo Scope:**
- 1 therapist (Dr. Sarah Johnson - T001) calls in sick
- 3 affected appointments need rescheduling
- 4 available providers (1 sick, 3 active)
- 3 patients with varying preferences

---

## Use Case 1: Trigger - Identify Affected Appointments

**Story:** Dr. Sarah Johnson calls in sick

**Actor:** Smart Scheduling Agent

**Trigger:** Therapist status change (T001 marked as "sick")

**Pre-conditions:**
- Dr. Sarah Johnson (T001) has 3 scheduled appointments
- Patients have different conditions and preferences
- System has access to appointment data

**Flow:**

1. System detects therapist unavailability (T001 status = "sick")
2. Query all appointments for therapist T001
3. Retrieve patient details for each appointment:
   - Patient demographics (name, age, gender)
   - Clinical condition and specialty required
   - Communication preferences (email/phone)
   - Scheduling preferences (days, times, location)
4. Calculate simple priority based on urgency
5. Return list of affected appointments

**Output:**
```
Affected Appointments for T001 (Dr. Sarah Johnson):

1. A001 - Maria Rodriguez (PAT001)
   - Condition: Post-surgical knee (orthopedic required)
   - Date: Nov 20, 10:00 AM
   - Priority: HIGH (surgical recovery)

2. A002 - John Davis (PAT002)  
   - Condition: Lower back pain (orthopedic required)
   - Date: Nov 21, 2:00 PM
   - Priority: MEDIUM (chronic condition)

3. A003 - Susan Lee (PAT003)
   - Condition: Hip replacement recovery (orthopedic required)
   - Date: Nov 22, 9:00 AM  
   - Priority: HIGH (post-surgical)

Total Affected: 3 appointments
```

**Success Criteria:**
- ✅ All 3 appointments identified
- ✅ Patient details retrieved
- ✅ Conditions and preferences loaded
- ✅ Processed within seconds

**Data Required:**
- `appointments.json`: All appointments for T001
- `patients.json`: Patient demographics and preferences
- `providers.json`: Provider status

---

## Use Case 2: Filter Candidates with Compliance Rules

**Story:** System filters qualified providers for Maria Rodriguez's appointment

**Actor:** Smart Scheduling Agent

**Input:** 
- Appointment A001 (Maria Rodriguez)
- Patient: Post-surgical knee, female, prefers female PT
- Available Providers: 3 active (P001, P003, P004)

**Pre-conditions:**
- Provider details are current (specialty, gender, location, capacity)
- Patient preferences are known

**Flow:**

1. Retrieve patient requirements:
   - Condition: Post-surgical knee → **requires orthopedic specialist**
   - Gender preference: **Female preferred**
   - Location: **Within 10 miles** of patient
   - Modality: In-person required

2. Retrieve provider details for 3 active providers:
   - P001: Dr. Emily Ross (Female, Orthopedic, 2 miles, 60% capacity)
   - P003: Dr. Anna Park (Female, Neurological, 15 miles, 72% capacity)  
   - P004: Dr. Michael Lee (Male, Orthopedic, 3.5 miles, 88% capacity)

3. Apply compliance filters:

   **Filter 1: Required Specialty**
   - Required: Orthopedic for post-surgical knee
   - ✅ Pass: P001 (orthopedic), P004 (orthopedic)
   - ❌ Eliminated: P003 (neurological - wrong specialty)

   **Filter 2: Gender Preference**  
   - Preferred: Female provider
   - ✅ Pass: P001 (female)
   - ⚠️ Warning: P004 (male - doesn't match preference but not eliminatory)

   **Filter 3: Location Constraint**
   - Required: Within 10 miles
   - ✅ Pass: P001 (2 miles), P004 (3.5 miles)
   - ❌ Already eliminated: P003 (15 miles)

   **Filter 4: Capacity Check**
   - Required: Not overloaded (< 90% capacity)
   - ✅ Pass: P001 (60%), P004 (88%)

4. Return qualified provider IDs

**Output:**
```
Qualified Providers for Maria Rodriguez (A001):

✅ P001: Dr. Emily Ross
   - Specialty: Orthopedic ✓
   - Gender: Female ✓  
   - Distance: 2.0 miles ✓
   - Capacity: 15/25 (60%) ✓

✅ P004: Dr. Michael Lee  
   - Specialty: Orthopedic ✓
   - Gender: Male (preference not met)
   - Distance: 3.5 miles ✓
   - Capacity: 22/25 (88%) ✓

Eliminated:
❌ P003: Dr. Anna Park - Wrong specialty (neurological vs orthopedic)
```

**Success Criteria:**
- ✅ All filters applied correctly
- ✅ At least 1 qualified candidate found
- ✅ Filter reasons logged
- ✅ Preference warnings noted

**Data Required:**
- `patients.json`: Patient preferences (condition, gender_preference, max_distance_miles)
- `providers.json`: Provider details (specialty, gender, distance, capacity)

---

## Use Case 3: Score and Rank Providers

**Story:** Rank the 2 qualified providers for Maria using multi-factor scoring

**Actor:** Smart Scheduling Agent

**Input:** 
- 2 qualified providers [P001, P004]
- Maria's profile and preferences
- Appointment details (date/time)

**Pre-conditions:**
- All providers passed compliance filters
- Patient preferences are known

**Flow:**

1. Define scoring factors (Total: 150 points):
   ```
   - Specialty Match: 40 points (exact specialty match)
   - Patient Preference: 30 points (gender, location)
   - Schedule Load: 25 points (lower load = better balance)
   - Continuity: 35 points (has patient seen provider before?)
   - Time Match: 20 points (matches patient's preferred time)
   ```

2. Score each provider:

   **Provider P001: Dr. Emily Ross**
   ```
   Specialty Match: 40/40 pts (Orthopedic specialist - exact match)
   Patient Preference: 30/30 pts
     - Gender: Female ✓ (+15 pts)
     - Location: 2 miles, very close ✓ (+15 pts)
   Schedule Load: 20/25 pts (60% capacity - good balance)
   Continuity: 0/35 pts (Maria has never seen Dr. Ross)
   Time Match: 20/20 pts (Tuesday 10 AM - matches Maria's preferred time)
   
   TOTAL: 110/150 pts
   Rank: #1 - EXCELLENT match
   ```

   **Provider P004: Dr. Michael Lee**
   ```
   Specialty Match: 40/40 pts (Orthopedic specialist - exact match)
   Patient Preference: 5/30 pts
     - Gender: Male ✗ (0 pts - Maria prefers female)
     - Location: 3.5 miles, acceptable ✓ (+5 pts)
   Schedule Load: 8/25 pts (88% capacity - nearly full)
   Continuity: 35/35 pts (Treated Maria's knee 2 years ago)
   Time Match: 0/20 pts (Only Thursday available, not Tuesday)
   
   TOTAL: 88/150 pts  
   Rank: #2 - GOOD option (strong continuity)
   ```

3. Rank providers by total score
4. Generate human-readable explanation

**Output:**
```
Ranked Candidates for Maria Rodriguez (A001):

🥇 #1: Dr. Emily Ross (110/150 pts) - RECOMMENDED
   Why: Perfect specialty match, meets gender preference, 
   ideal location (2 mi), available Tuesday morning
   
🥈 #2: Dr. Michael Lee (88/150 pts) - ALTERNATIVE  
   Why: Treated Maria before (good continuity), but doesn't 
   match gender preference and schedule is nearly full

Recommendation: Offer Dr. Emily Ross first
```

**Success Criteria:**
- ✅ All 5 scoring factors calculated
- ✅ Providers ranked by score
- ✅ Clear reasoning provided
- ✅ At least 1 provider scores >70 points

**Data Required:**
- `patients.json`: Preferences (gender_preference, preferred_days, preferred_time_block, prior_providers)
- `providers.json`: Provider details (specialty, gender, capacity_utilization, distance_from_maria)
- `appointments.json`: Appointment timing

---

## Use Case 4: Send Offer and Get Patient Consent

**Story:** Send offer to Maria via email and handle her response

**Actor:** Patient Engagement Agent

**Input:**
- Appointment A001
- Top candidate: Dr. Emily Ross (110 pts)
- Patient communication preference: Email

**Pre-conditions:**
- Patient has valid email address
- Communication service is available

**Flow:**

1. Retrieve patient communication preferences
   - Primary: Email (maria.r@email.com)
   - Secondary: Phone (+1-555-234-5678)

2. Compose personalized email message:
   ```
   Hi Maria,

   Dr. Sarah Johnson is unavailable. We'd like to reschedule you 
   with Dr. Emily Ross on 2024-11-20 at 10:00 AM.

   Please choose one of the following:
   ✅ CONFIRM: [Click here to confirm]
   ❌ DECLINE: [Click here to see other options]
   ℹ️  MORE INFO: [Click here to learn about Dr. Ross]

   Thank you,
   Metro PT Team
   ```

3. Send via email (mock for demo)

4. Simulate patient response: **"YES"** (in demo, auto-responds after simulated delay)

5. Upon YES response:
   - Mark consent as granted
   - Log response time
   - Proceed to booking stage

**Scenarios:**

**Scenario A: Patient responds "YES"** ✅ (happens in demo)
- Consent granted
- Proceed to booking
- Send confirmation

**Scenario B: Patient responds "NO"** (not in demo)
- Log decline
- Would offer candidate #2 (Dr. Michael Lee)

**Scenario C: Patient requests "INFO"** (simulated in demo)
- Show provider details via mock webpage
- Wait for YES/NO response

**Output:**
```
Consent Result for A001:
- Patient: Maria Rodriguez
- Offered Provider: Dr. Emily Ross  
- Channel Used: Email
- Response: YES ✓
- Response Time: 45 minutes (simulated)
- Consent Granted: True
- Next Step: Book appointment
```

**Success Criteria:**
- ✅ Email sent successfully
- ✅ Response captured
- ✅ Consent logged with timestamp
- ✅ Clear audit trail

**Data Required:**
- `patients.json`: Communication preferences (email, phone, communication_channel_primary)
- `providers.json`: Provider details for message
- Mock email service (simulated)

---

## Use Case 5: Book Appointment and Send Confirmation

**Story:** System books Maria with Dr. Emily Ross and sends confirmation

**Actor:** Patient Engagement Agent + Domain Server

**Input:**
- Appointment A001  
- Confirmed provider: Dr. Emily Ross (P001)
- Patient consent: YES

**Pre-conditions:**
- Patient has confirmed consent
- Provider is still available
- Booking system is operational

**Flow:**

1. Prepare booking data:
   ```json
   {
     "appointment_id": "A001",
     "patient_id": "PAT001", 
     "provider_id": "P001",
     "date": "2024-11-20",
     "time": "10:00 AM",
     "status": "scheduled",
     "confirmation_number": "CONF-AUTO"
   }
   ```

2. Update appointment in JSON database:
   - Change provider from T001 → P001
   - Update status to "scheduled"
   - Add confirmation number

3. Send confirmation email to patient:
   ```
   Confirmed! Your appointment with Dr. Emily Ross is scheduled 
   for 2024-11-20 at 10:00 AM at Metro PT Main Clinic.

   Reply CANCEL if you need to reschedule.

   - Metro PT
   ```

4. Notify stakeholders (simulated):
   - ✅ Patient: Confirmation sent
   - ✅ New Provider (Dr. Ross): Notified of new patient
   - ✅ Front Desk: Updated schedule

**Output:**
```
Booking Complete for A001:
- Status: SUCCESS ✓
- Patient: Maria Rodriguez (PAT001)
- Old Provider: Dr. Sarah Johnson (T001) - sick
- New Provider: Dr. Emily Ross (P001)  
- Date/Time: Nov 20, 2024 at 10:00 AM
- Confirmation: CONF-AUTO
- Patient Notified: Yes (email sent)
- Provider Notified: Yes
- EMR Updated: Yes
```

**Success Criteria:**
- ✅ Appointment updated in database
- ✅ Confirmation number generated
- ✅ Patient receives confirmation
- ✅ All stakeholders notified
- ✅ Audit trail complete

**Data Required:**
- `appointments.json`: Update appointment record
- `patients.json`: Patient email for confirmation
- `providers.json`: New provider details
- JSON Domain Server for booking

---

## Use Case 6: Generate Audit Log and Complete Session

**Story:** System confirms all actions and creates audit trail

**Actor:** Smart Scheduling Agent

**Input:** All events from processing 3 appointments

**Pre-conditions:**
- All workflows completed
- All appointments have final status
- All notifications sent

**Flow:**

1. Collect all workflow events:
   - Stage 1: Trigger (T001 unavailable, 3 appointments found)
   - Stage 2: Filtering (2 qualified providers)
   - Stage 3: Scoring (Dr. Ross ranked #1)
   - Stage 4: Consent (Patient said YES)
   - Stage 5: Booking (Appointment confirmed)
   - Stage 6: Audit (This stage)

2. Generate audit log:
   ```json
   {
     "session_id": "SESSION-T001-001",
     "therapist_id": "T001",
     "therapist_name": "Dr. Sarah Johnson",
     "start_time": "2024-11-19T10:00:00",
     "end_time": "2024-11-19T10:05:32",
     "duration_seconds": 332,
     "appointments_processed": 1,
     "appointments_rebooked": 1,
     "appointments_pending": 2,
     "success_rate": 1.0,
     "events": [
       {"stage": "trigger", "status": "success", "timestamp": "..."},
       {"stage": "filter", "status": "success", "timestamp": "..."},
       {"stage": "score", "status": "success", "timestamp": "..."},
       {"stage": "consent", "status": "success", "timestamp": "..."},
       {"stage": "booking", "status": "success", "timestamp": "..."}
     ]
   }
   ```

3. Verify EMR updates:
   - ✅ Appointment A001: Provider updated T001 → P001
   - ⏳ Appointment A002: Pending (would process next)
   - ⏳ Appointment A003: Pending (would process next)

4. Generate summary for front desk:
   ```
   Session Complete: T001 Replacement
   
   ✅ Processed: 1 appointment
   ✅ Rebooked: Maria Rodriguez (A001) → Dr. Emily Ross
   ⏳ Pending: 2 appointments need processing
   
   Time: 5 minutes 32 seconds
   Status: SUCCESS
   ```

**Output:**
```
Audit Complete:
✓ Session ID: SESSION-T001-001
✓ Appointments processed: 1/3
✓ Rebooked successfully: 1
✓ Pending: 2
✓ Audit log created and saved
✓ EMR verified up-to-date
✓ All stakeholders notified
✓ Duration: 5m 32s

Status: COMPLETE
```

**Success Criteria:**
- ✅ Complete audit trail exists
- ✅ All events logged with timestamps
- ✅ EMR verified
- ✅ Summary generated
- ✅ Session marked complete

**Data Required:**
- Session state (in-memory during workflow)
- Event logs from all stages
- Final appointment status from JSON

---

## Use Case Summary - Demo Version

| Use Case | Demo Scenario | Data Used | Success Metric |
|----------|--------------|-----------|----------------|
| **1. Trigger** | T001 sick, find 3 appointments | appointments.json, patients.json | All 3 found ✅ |
| **2. Filtering** | Filter 3 providers for Maria | providers.json, patients.json | 2 qualified ✅ |
| **3. Scoring** | Rank P001 vs P004 | All JSON files | Dr. Ross #1 ✅ |
| **4. Consent** | Send email to Maria, get YES | patients.json, mock email | Consent ✅ |
| **5. Booking** | Book A001 with P001 | appointments.json update | Booked ✅ |
| **6. Audit** | Generate session log | All events | Log created ✅ |

---

## Integration Flow

```
[UC1: Trigger]
  Dr. Sarah Johnson (T001) marked sick
  ↓ Find affected appointments
  3 appointments found: A001, A002, A003
  ↓
[UC2: Filtering]
  Process A001 (Maria Rodriguez)
  ↓ Filter 3 active providers
  2 qualified: P001, P004
  ↓
[UC3: Scoring]  
  Score and rank providers
  ↓ Calculate scores (150 pts max)
  Winner: P001 (110 pts)
  ↓
[UC4: Consent]
  Send offer to Maria via email
  ↓ Wait for response
  Response: YES ✓
  ↓
[UC5: Booking]
  Book appointment A001 with P001
  ↓ Update EMR
  Confirmation sent ✓
  ↓
[UC6: Audit]
  Generate audit log
  ↓ Verify all actions
  Session complete ✓
```

---

## What This Demo Shows

✅ **End-to-end workflow** - All 6 stages working  
✅ **Real JSON data** - No hardcoded responses  
✅ **Compliance filtering** - Specialty, gender, location, capacity  
✅ **Multi-factor scoring** - 5 factors, 150 point scale  
✅ **Patient communication** - Email with clickable links  
✅ **EMR integration** - JSON database updates  
✅ **Audit trail** - Complete session logging  
✅ **Receptionist-friendly UI** - Clear summaries and next steps  

## What This Demo Doesn't Show (Out of Scope)

❌ Multiple appointment processing (shows 1 of 3)  
❌ Backfill/waitlist automation (UC5 alternative flow)  
❌ SMS communication (uses email only)  
❌ High no-show risk targeting  
❌ HOD fallback assignment  
❌ Real-time provider availability checking  
❌ POC/Medicare compliance validation  
❌ Revenue impact calculation  

---

**This simplified version matches your current data exactly while still demonstrating the complete 6-stage intelligent workflow!** 🎯

