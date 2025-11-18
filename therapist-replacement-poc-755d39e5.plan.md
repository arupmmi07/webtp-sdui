<!-- 755d39e5-2192-470b-9c17-8aee17e09c34 c423ee5f-fba2-469d-b60c-2457965c4d51 -->
# Therapist Replacement POC - Complete Actionable Plan

## Overview

Build a production-ready POC that demonstrates automated therapist replacement with intelligent provider matching, compliance checking, and patient engagement. The system reads matching rules from knowledge documents (PDF), uses MCP for pluggable APIs, employs LLM-orchestrated agents for dynamic workflow execution, and handles all 6 use cases with complete audit trails.

## Personas & User Stories

### Persona 1: Sarah Chen - Front Desk Manager

**Profile:**

- Role: Office Manager at Metro Physical Therapy
- Age: 42, Tech-savvy: Medium
- Manages: 5 therapists, 200+ active patients
- Pain Points: Manual rescheduling takes 3+ hours per therapist departure, revenue loss from empty slots
- Goals: Minimize admin work, prevent empty slots, keep patients happy, maintain compliance

**User Stories:**

1. As Sarah, I want to be notified immediately when a therapist calls in sick, so I can start reassignment quickly
2. As Sarah, I want the system to prioritize patients who are likely to no-show, so I can fill slots that would otherwise go empty
3. As Sarah, I want to see an audit trail of all changes, so I can answer patient questions about rescheduled appointments
4. As Sarah, I want the system to handle payer compliance automatically, so I don't accidentally violate insurance rules

### Persona 2: Dr. Emily Ross - Physical Therapist

**Profile:**

- Role: Senior Physical Therapist, specializes in orthopedics
- Age: 38, Experience: 12 years
- Patient Load: 25 active patients (max capacity)
- Concerns: Patient continuity, appropriate skill match, work-life balance
- Goals: See patients matching her expertise, maintain manageable schedule, provide excellent care

**User Stories:**

1. As Dr. Ross, I want patients reassigned to me to match my specialization, so I can provide the best care
2. As Dr. Ross, I want to see patients I've treated before when possible, so I can maintain continuity of care
3. As Dr. Ross, I don't want to be overloaded beyond my capacity, so the system should balance assignments
4. As Dr. Ross, I want to know patient preferences before meeting them, so I can prepare appropriately

### Persona 3: Maria Rodriguez - Patient

**Profile:**

- Age: 55, Occupation: Teacher
- Condition: Post-surgical knee rehabilitation (8 weeks post-op)
- Preferences: Female therapist, morning appointments, text messages
- Insurance: Medicare (requires prior authorization for PT)
- Tech comfort: Medium (uses smartphone)
- Concerns: Continuity, convenience, communication, privacy

**User Stories:**

1. As Maria, I want to be notified quickly if my therapist is unavailable, so I'm not surprised when I show up
2. As Maria, I want a female therapist if possible, so I feel comfortable during treatment
3. As Maria, I want to approve the new therapist via text message, so I don't have to call the office
4. As Maria, I want my appointment on the same day/time if possible, so it doesn't disrupt my teaching schedule
5. As Maria, I want to know the new therapist's qualifications, so I feel confident in their care

### Persona 4: Dr. Robert Williams - Head of Department (HOD)

**Profile:**

- Role: Clinical Director, 20+ years experience
- Responsibilities: Oversee all therapists, handle complex cases, ensure quality of care
- Availability: Often fully booked, handles escalations
- Goals: Ensure no patient is unassigned, maintain quality standards, minimize complaints

**User Stories:**

1. As Dr. Williams, I want to be the fallback for any patient who can't be matched, so no patient is left without care
2. As Dr. Williams, I want to review cases where no match was found, so I can manually intervene if needed
3. As Dr. Williams, I want to see why patients were assigned to me, so I can understand the system's decision-making
4. As Dr. Williams, I want to track system performance metrics, so I can identify areas for improvement

### Persona 5: John Davis - High No-Show Risk Patient

**Profile:**

- Age: 32, Occupation: Construction worker (variable schedule)
- Condition: Chronic lower back pain
- History: 3 no-shows in past 6 months (40% no-show rate)
- Preferences: Flexible timing, prefers phone calls
- Insurance: Workers Compensation (employer-paid)
- Concerns: Schedule conflicts, forgets appointments

**User Stories:**

1. As John, I want appointment reminders via phone call, so I don't forget
2. As John, I want flexible appointment times that work with my variable schedule
3. As John, I want to be offered earlier appointments when they become available, so I can get treatment sooner

## Complete Use Case Mapping

### Use Case 1: Trigger - Identify Affected Appointments with Priority

**Story:** Dr. Sarah Johnson calls in sick for the next 2 weeks

**Actor:** System (Automated Detection)

**Trigger:** Therapist status change in EMR

**Pre-conditions:**

- Dr. Johnson has 15 scheduled appointments
- Patients have varying no-show risk profiles
- Some patients have POC expiration dates approaching

**Flow:**

1. System detects therapist unavailability event
2. Query all appointments for therapist T123 (Dr. Johnson) for next 14 days
3. For each appointment, calculate priority score:
   ```
   Priority Score = (no_show_risk * 40) + (poc_urgency * 30) + (revenue_value * 20) + (patient_satisfaction_risk * 10)
   
   Where:
   - no_show_risk: 0-1 (based on patient history)
   - poc_urgency: 0-1 (1 = POC expires within 7 days)
   - revenue_value: 0-1 (normalized appointment value)
   - patient_satisfaction_risk: 0-1 (VIP patients, complaints history)
   ```

4. Retrieve patient data:

                                                                                                                                                                                                - No-show history (last 12 months)
                                                                                                                                                                                                - Insurance/payer type
                                                                                                                                                                                                - POC expiration dates
                                                                                                                                                                                                - Communication preferences
                                                                                                                                                                                                - Clinical condition/urgency

5. Sort appointments by priority score (descending)
6. Emit "trigger_detected" event with prioritized list

**Output:**

```
Prioritized Appointments:
1. A001 - Maria Rodriguez - Priority: 87 (no-show: 0.8, POC expires: 7 days)
2. A005 - John Davis - Priority: 78 (no-show: 0.9, chronic condition)
3. A003 - Susan Lee - Priority: 65 (no-show: 0.3, POC expires: 10 days)
...
15. A012 - Tom Brown - Priority: 22 (no-show: 0.1, standard)

High Priority: 5 appointments
Medium Priority: 7 appointments
Low Priority: 3 appointments
```

**Success Criteria:**

- All 15 appointments identified
- No-show risk calculated for each
- POC urgency flagged
- Sorted by priority
- Event emitted within 30 seconds

**Knowledge Required:**

- No-show risk calculation algorithm
- POC urgency thresholds
- Priority scoring weights

---

### Use Case 2: Match Candidate Filtering with Compliance

**Story:** System filters qualified providers for Maria Rodriguez's post-surgical knee appointment

**Actor:** Matching Agent

**Input:**

- Appointment A001
- Patient: Maria Rodriguez (Medicare, post-surgical knee, female, prefers female PT)
- Available Providers: 8 therapists

**Pre-conditions:**

- All providers have current licenses
- Provider skills and certifications are up-to-date in system
- Payer rules are configured in knowledge base

**Flow:**

1. Retrieve patient details from Patient API (MCP):

                                                                                                                                                                                                - Insurance: Medicare (requires Medicare-approved provider)
                                                                                                                                                                                                - Condition: Post-surgical knee (requires orthopedic certification)
                                                                                                                                                                                                - POC Status: Active, expires 2025-12-15
                                                                                                                                                                                                - Location preference: Within 10 miles of home
                                                                                                                                                                                                - Modality: In-person required (no telehealth)

2. Retrieve provider details from Provider API (MCP):

                                                                                                                                                                                                - For each of 8 providers, check:
                                                                                                                                                                                                                                                                                                                                - Active license status
                                                                                                                                                                                                                                                                                                                                - Certifications/specializations
                                                                                                                                                                                                                                                                                                                                - Current patient load vs. max capacity
                                                                                                                                                                                                                                                                                                                                - Geographic location
                                                                                                                                                                                                                                                                                                                                - Telehealth vs. in-person availability
                                                                                                                                                                                                                                                                                                                                - Payer acceptance (Medicare approved?)

3. Apply hard constraint filters (eliminates non-qualified):

**Filter 1: Required Skills/Certifications**

                                                                                                                                                                                                - Required: Orthopedic PT certification for post-surgical knee
                                                                                                                                                                                                - Pass: 6/8 providers (2 eliminated: pediatric specialists)

**Filter 2: License & Privileges**

                                                                                                                                                                                                - Required: Active state license, hospital privileges
                                                                                                                                                                                                - Pass: 6/6 providers

**Filter 3: POC Status Validation**

                                                                                                                                                                                                - Check: Provider authorized under Maria's Medicare POC
                                                                                                                                                                                                - Pass: 5/6 providers (1 eliminated: not on approved POC provider list)

**Filter 4: Payer Rules Compliance**

                                                                                                                                                                                                - Required: Medicare-approved provider (NPI registered with Medicare)
                                                                                                                                                                                                - Pass: 5/5 providers

**Filter 5: Location Constraint**

                                                                                                                                                                                                - Required: Within 10 miles of patient's home address
                                                                                                                                                                                                - Pass: 4/5 providers (1 eliminated: 15 miles away)

**Filter 6: Telehealth Flag**

                                                                                                                                                                                                - Required: In-person availability (patient requires in-person)
                                                                                                                                                                                                - Pass: 4/4 providers

**Filter 7: Availability Check**

                                                                                                                                                                                                - Required: Open slot within ±3 days of original appointment (Tuesday 11/20)
                                                                                                                                                                                                - Pass: 3/4 providers (1 eliminated: fully booked Mon-Thu)

**Filter 8: Capacity Check**

                                                                                                                                                                                                - Required: Current load < max capacity (not overloaded)
                                                                                                                                                                                                - Pass: 3/3 providers

4. Emit "candidates_filtered" event with qualified provider IDs

**Output:**

```
Qualified Providers for A001:
- P001: Dr. Emily Ross (Female, Orthopedic, 15/25 patients, Tuesday 10 AM available)
- P004: Dr. Michael Lee (Male, Orthopedic, 22/25 patients, Tuesday 10 AM available)
- P006: Dr. Anna Park (Female, Sports Medicine + Orthopedic, 18/25 patients, Tuesday 2 PM available)

Eliminated Providers:
- P002: Not orthopedic certified (eliminated: skills)
- P003: Not orthopedic certified (eliminated: skills)
- P005: Not on POC approved list (eliminated: POC status)
- P007: Location too far (eliminated: location)
- P008: No availability within ±3 days (eliminated: availability)
```

**Success Criteria:**

- All 8 filters applied correctly
- Compliance rules enforced (POC, payer)
- At least 1 qualified candidate found
- Filter reasons logged for audit

**Knowledge Required:**

- Payer rules by insurance type (knowledge doc)
- POC validation criteria (knowledge doc)
- Required certifications by condition (knowledge doc)
- Location/distance constraints (config)

---

### Use Case 3: Compliance and Score Gating

**Story:** Rank the 3 qualified providers for Maria using multi-factor scoring

**Actor:** Matching Agent (Scoring Module)

**Input:**

- 3 qualified providers [P001, P004, P006]
- Maria's profile and preferences
- Appointment details

**Pre-conditions:**

- All providers passed compliance filters
- Patient preferences are known
- Provider history with patient is available

**Flow:**

1. Read scoring weights from knowledge document:
   ```
   Scoring Factors (Total: 150 points):
   - Continuity Score: 40 points (has patient seen this provider before?)
   - Specialty Match: 35 points (exact specialty vs. general)
   - Patient Preference Fit: 30 points (gender, age, language, etc.)
   - Schedule Load Balance: 25 points (lower load = higher score)
   - Day/Time Match: 20 points (matches patient's preferred day/time)
   ```

2. Score each provider:

**Provider P001: Dr. Emily Ross**

   ```
   Continuity: 0/40 pts (Maria has never seen Dr. Ross)
   Specialty: 35/35 pts (Orthopedic specialist, exact match for post-surgical knee)
   Patient Preference: 30/30 pts
     - Gender match: +15 pts (female provider, Maria prefers female)
     - Same clinic location: +10 pts
     - Age similarity: +5 pts (both 50s)
   Schedule Load: 20/25 pts (15/25 patients = 60% capacity, well-balanced)
   Day/Time Match: 20/20 pts (Tuesday 10 AM, Maria's preferred day/time)
   
   TOTAL: 105/150 pts
   Recommendation: EXCELLENT match despite no prior history
   ```

**Provider P004: Dr. Michael Lee**

   ```
   Continuity: 40/40 pts (Treated Maria 2 years ago for same knee, excellent history)
   Specialty: 30/35 pts (General PT with orthopedic training, not specialist)
   Patient Preference: 5/30 pts
     - Gender match: 0 pts (male provider, Maria prefers female)
     - Same clinic: +5 pts
   Schedule Load: 8/25 pts (22/25 patients = 88% capacity, near max)
   Day/Time Match: 0/20 pts (Thursday 3 PM only, Maria prefers Tuesday mornings)
   
   TOTAL: 83/150 pts
   Recommendation: GOOD continuity but poor preference match
   ```

**Provider P006: Dr. Anna Park**

   ```
   Continuity: 0/40 pts (Never seen Maria)
   Specialty: 32/35 pts (Sports Medicine + Orthopedic, very qualified)
   Patient Preference: 25/30 pts
     - Gender match: +15 pts (female)
     - Different clinic location: 0 pts (10 miles away vs. 2 miles for others)
     - Younger age: +10 pts
   Schedule Load: 18/25 pts (18/25 patients = 72% capacity)
   Day/Time Match: 10/20 pts (Tuesday 2 PM, right day but afternoon not preferred)
   
   TOTAL: 85/150 pts
   Recommendation: GOOD alternative if Dr. Ross declines
   ```

3. Rank providers by total score
4. Generate explanation for each score
5. Emit "candidates_scored" event with ranked list

**Output:**

```
Ranked Candidates for Maria Rodriguez (A001):
1. Dr. Emily Ross (105 pts) - RECOMMENDED
   Reasons: Perfect specialty match, gender preference met, ideal time slot, good availability
   
2. Dr. Anna Park (85 pts) - GOOD ALTERNATIVE
   Reasons: Female provider, well-qualified, slightly less convenient time
   
3. Dr. Michael Lee (83 pts) - CONTINUITY OPTION
   Reasons: Has treated patient before, but doesn't match preferences well

Scoring Details Logged: Yes
Explanation Available: Yes
```

**Success Criteria:**

- All 5 scoring factors applied
- Scores calculated correctly
- Providers ranked by total score
- Human-readable reasons generated
- At least 1 provider scores >70 points

**Knowledge Required:**

- Scoring weights and formulas (knowledge doc)
- Patient preference definitions (knowledge doc)
- Continuity scoring rules (knowledge doc)

---

### Use Case 4: Automated Patient Offer Flow with Multi-Channel

**Story:** Send offer to Maria via her preferred communication channel and handle her response

**Actor:** Consent Agent

**Input:**

- Appointment A001
- Top candidate: Dr. Emily Ross (105 pts)
- Patient communication preference: SMS (primary), Email (backup)

**Pre-conditions:**

- Patient has valid phone number and email
- Notification service (MCP) is operational
- Consent timeout is configured (24 hours)

**Flow:**

1. Retrieve patient communication preferences from Patient API:
   ```
   Maria's Preferences:
   - Primary: SMS to +1-555-0123
   - Secondary: Email to maria.rodriguez@email.com
   - Tertiary: Phone call (if no response after 24h)
   - Language: English
   - Preferred contact time: 8 AM - 6 PM
   ```

2. Compose personalized message using patient and provider details:
   ```
   SMS Message:
   "Hi Maria, Dr. Johnson is unavailable for your Tue 11/20 10 AM appt. 
   We've matched you with Dr. Emily Ross (female, orthopedic specialist, 
   same time/location). Reply YES to confirm, NO for other options, 
   or INFO for more details about Dr. Ross."
   ```

3. Send via Notification API (MCP) - SMS channel:
   ```
   Request:
   {
     "channel": "sms",
     "to": "+1-555-0123",
     "message": "...",
     "appointment_id": "A001",
     "requires_response": true,
     "timeout_hours": 24
   }
   
   Response:
   {
     "message_id": "MSG_20251115_093045_A001",
     "status": "sent",
     "sent_at": "2025-11-15T09:30:45Z"
   }
   ```

4. Start timeout timer (24 hours) and listen for response

5. **Scenario A: Patient responds "YES"** (happens at 10:15 AM, 45 min later)
   ```
   Response received: "YES"
   Timestamp: 2025-11-15T10:15:32Z
   
   Actions:
   a) Book appointment via Appointment API (MCP):
      - Update A001: new provider = P001 (Dr. Emily Ross)
      - Status: CONFIRMED
      - Lock calendar slot
   
   b) Send confirmation SMS:
      "Confirmed! Your Tue 11/20 10 AM appt with Dr. Emily Ross at 
      Metro PT (123 Main St). Reply CANCEL if you need to change."
   
   c) Notify Dr. Emily Ross:
      "New patient: Maria Rodriguez, post-surgical knee rehab, 
      Tue 11/20 10 AM. Previous notes from Dr. Johnson attached."
   
   d) Notify Sarah (front desk):
      "A001 successfully rebooked - Maria Rodriguez → Dr. Ross"
   
   e) Log consent with timestamp
   
   f) Emit "appointment_booked" event
   ```

6. **Scenario B: Patient responds "NO"** (offer next candidate)
   ```
   Response received: "NO"
   Timestamp: 2025-11-15T11:20:00Z
   
   Actions:
   a) Log decline for Dr. Emily Ross
   
   b) Offer candidate #2 (Dr. Anna Park):
      "Okay, how about Dr. Anna Park (female, sports medicine/orthopedic) 
      on Tue 11/20 at 2 PM (same day, afternoon)? Reply YES or NO."
   
   c) Wait for response again (24h timeout)
   
   d) If all 3 candidates declined → Emit "consent_declined_all" event
   ```

7. **Scenario C: Patient responds "INFO"** (provide more details)
   ```
   Response received: "INFO"
   
   Actions:
   a) Send detailed provider info:
      "Dr. Emily Ross: 12 years experience, orthopedic specialist, 
      Stanford-trained, 4.9/5 patient rating. View full profile: 
      [link]. Ready to book? Reply YES or NO."
   
   b) Continue waiting for YES/NO response
   ```

8. **Scenario D: No response after 24h** (timeout)
   ```
   Timeout reached: 2025-11-16T09:30:45Z
   
   Actions:
   a) Send reminder via secondary channel (Email):
      Subject: "Action Required: Confirm Your Rescheduled PT Appointment"
      Body: [Same offer details with YES/NO links]
   
   b) Wait additional 12 hours
   
   c) If still no response:
      - Emit "consent_timeout" event
      - Trigger backfill workflow
      - Flag for manual follow-up (Sarah to call)
   ```


**Output (Success Case):**

```
Consent Result for A001:
- Patient: Maria Rodriguez
- Offered Provider: Dr. Emily Ross
- Channel Used: SMS
- Message ID: MSG_20251115_093045_A001
- Response: YES
- Response Time: 45 minutes
- Appointment Status: CONFIRMED
- Confirmation Sent: Yes
- Stakeholders Notified: Patient, Provider, Front Desk
- Next Action: None (workflow complete)
```

**Success Criteria:**

- Message sent via preferred channel
- Response captured within timeout
- Appointment booked in EMR
- All stakeholders notified
- Consent logged with timestamp
- Audit trail complete

**Knowledge Required:**

- Communication channel configuration (knowledge doc)
- Message templates (knowledge doc)
- Timeout policies (config)
- Escalation rules (knowledge doc)

---

### Use Case 5: Waitlist & Backfill Automation with High No-Show Targeting

**Story:** John Davis declines all 3 providers, system backfills his slot and finds him an alternative

**Actor:** Backfill Agent

**Input:**

- Appointment A002 - all 3 candidates declined by patient
- John Davis profile: High no-show risk (0.9), workers comp, flexible schedule

**Pre-conditions:**

- John's original slot is now freed: Monday 11/18 2 PM
- High no-show risk patient list is available
- John's availability windows are in system

**Flow:**

**Part 1: Fill the Freed Slot**

1. Add freed slot to Intelligent Waitlist:
   ```
   Waitlist Entry:
   - Slot ID: SLOT_20251118_1400
   - Date/Time: Monday 11/18, 2 PM
   - Duration: 60 minutes
   - Provider: Any qualified for lower back pain (John's original condition)
   - Location: Metro PT Main Clinic
   - Available For: Any patient needing lower back pain treatment
   ```

2. Query high no-show risk patients who need similar treatment:
   ```
   Query Criteria:
   - No-show risk >= 0.6
   - Condition: Lower back pain OR related
   - Current appointment: Scheduled >3 days out (would benefit from earlier slot)
   - Insurance: Active
   
   Results:
   - P045: Sarah Miller (no-show risk 0.75, appointment 11/25)
   - P067: Tom Anderson (no-show risk 0.65, appointment 11/22)
   - P089: Lisa Wong (no-show risk 0.70, appointment 11/24)
   ```

3. Offer slot to high-risk patients (prioritized by risk score):

**Offer to P045 (Sarah Miller, highest risk 0.75):**

   ```
   Phone Call (automated IVR):
   "Hi Sarah, this is Metro PT. We have an earlier opening on Monday 11/18 
   at 2 PM for your lower back pain treatment. This is 7 days earlier than 
   your current appointment. Press 1 to accept, 2 to keep your current 
   appointment, 3 to speak with someone."
   
   Response: Press 1 (ACCEPT)
   Timestamp: 2025-11-15T14:22:00Z
   ```

4. Book Sarah into freed slot:
   ```
   Actions:
   a) Update Sarah's appointment:
      - Old: 11/25 3 PM → Canceled
      - New: 11/18 2 PM → CONFIRMED
      - Provider: Dr. Michael Lee (available for that slot)
   
   b) Send confirmation:
      "Confirmed! Your appointment moved to Mon 11/18 2 PM with Dr. Lee. 
      We'll send a reminder the day before."
   
   c) Send extra reminder (because high no-show risk):
      Schedule reminders:
      - 48h before: SMS reminder
      - 24h before: Phone call reminder
      - 3h before: Final SMS reminder
   
   d) Log backfill success
   ```


**Part 2: Reschedule John (Original Patient)**

5. Retrieve John's availability windows from Patient API:
   ```
   John Davis Availability:
   - Preferred: Mon/Wed/Fri (construction schedule varies)
   - Time: Morning preferred (7-11 AM) or late afternoon (4-6 PM)
   - Cannot do: Tuesday (standing meeting)
   - Flexibility: High (can adjust if needed)
   - Note: "Call me, I forget to check texts" - prefers phone
   ```

6. Search for slots matching John's availability + qualified providers:
   ```
   Search Criteria:
   - Days: Monday, Wednesday, Friday
   - Times: 7-11 AM or 4-6 PM
   - Date Range: Within next 2 weeks
   - Provider: Qualified for lower back pain treatment
   - Provider History: Preferably someone John has seen before
   
   Results Found:
   - Option 1: Wed 11/20 8 AM with Dr. Anna Park (John saw her 6 months ago)
   - Option 2: Fri 11/22 5 PM with Dr. Michael Lee (new provider)
   - Option 3: Mon 11/25 9 AM with Dr. Anna Park
   ```

7. Auto-propose best match via preferred channel (phone call):
   ```
   Automated Phone Call to John:
   "Hi John, this is Metro PT. We couldn't match you with your original 
   Monday appointment. We found Wednesday 11/20 at 8 AM with Dr. Park - 
   you saw her before for your back pain. Press 1 to confirm, 2 to hear 
   other times, 3 to speak with someone."
   
   John Response: Press 1 (CONFIRM)
   ```

8. Book John's new appointment:
   ```
   Actions:
   a) Create new appointment:
      - A002_NEW: Wed 11/20 8 AM
      - Provider: Dr. Anna Park (P006)
      - Status: CONFIRMED
      - Notes: "Rescheduled from 11/18, patient confirmed via phone"
   
   b) Set high-priority reminders (John's no-show risk 0.9):
      - 72h before: Phone call reminder
      - 24h before: SMS + Phone call
      - Morning of: Phone call at 7 AM
   
   c) Notify Dr. Anna Park:
      "Returning patient: John Davis, chronic lower back pain, you treated 
      him 6 months ago. Wed 11/20 8 AM. Previous notes attached."
   
   d) Log reschedule success
   ```


**Alternative Flow: If No Match Found for John**

9. If no availability match found:
   ```
   Actions:
   a) Assign to HOD (Dr. Robert Williams):
      - Find any HOD slot (even if fully booked, HOD is fallback)
      - Create appointment with HOD
      - Flag as "overflow - HOD assignment"
   
   b) Notify HOD:
      "Overflow patient assigned: John Davis, lower back pain, high 
      no-show risk (0.9). No qualified provider available within 
      his availability windows. Please review."
   
   c) Flag for manual review:
      - Alert Sarah (front desk): "A002 requires manual follow-up"
      - Reason: "No provider match found, assigned to HOD"
      - Action needed: "Call patient to discuss alternatives"
   
   d) Create manual task:
      Task ID: MANUAL_A002
      Assignee: Sarah Chen
      Priority: Medium
      Due: Within 24 hours
      Details: "Call John Davis to find mutually acceptable time"
   ```


**Output (Success Case):**

```
Backfill Results for A002:

Part 1 - Freed Slot Filled:
- Original Patient: John Davis (declined all options)
- Freed Slot: Mon 11/18 2 PM
- Backfilled With: Sarah Miller (high no-show risk 0.75)
- Time to Fill: 4 hours 52 minutes
- Revenue Preserved: $120 (slot didn't go empty)

Part 2 - Original Patient Rescheduled:
- Patient: John Davis
- New Appointment: Wed 11/20 8 AM with Dr. Anna Park
- Match Quality: GOOD (continuity + availability match)
- Extra Reminders: 3 scheduled (high no-show risk mitigation)

System Impact:
- Empty slots prevented: 1
- High no-show risk patients helped: 2 (Sarah got earlier, John got reminders)
- Revenue impact: +$120 (freed slot filled)
- Manual intervention: None required
```

**Success Criteria:**

- Freed slot filled within 6 hours
- High no-show risk patient prioritized
- Original patient rescheduled successfully
- Availability windows respected
- Extra reminders set for high-risk patients
- HOD fallback used only if no other option

**Knowledge Required:**

- Waitlist prioritization rules (knowledge doc)
- No-show risk thresholds (config)
- Availability window matching logic (knowledge doc)
- HOD assignment criteria (knowledge doc)
- Reminder frequency by risk level (config)

---

### Use Case 6: Final Appointment Reconciliation & Audit

**Story:** System confirms all actions and creates comprehensive audit trail

**Actor:** Orchestrator (automatic logging across all agents)

**Input:** All events from processing 15 appointments (A001-A015)

**Pre-conditions:**

- All workflows completed (some booked, some rescheduled, some HOD-assigned)
- All stakeholder notifications sent
- All EMR updates completed

**Flow:**

1. Aggregate all event logs from entire session:
   ```
   Session aggregation:
   - Session ID: SESSION_2025-11-15_090000
   - Trigger: Therapist T123 (Dr. Sarah Johnson) unavailable
   - Duration: 2025-11-15 09:00:00 to 2025-11-15 16:45:00 (7h 45m)
   - Total Appointments Processed: 15
   - Total Events Logged: 247
   ```

2. Generate comprehensive audit log:
```json
{
  "session_id": "SESSION_2025-11-15_090000",
  "session_start": "2025-11-15T09:00:00Z",
  "session_end": "2025-11-15T16:45:00Z",
  "total_duration_minutes": 465,
  
  "trigger": {
    "timestamp": "2025-11-15T09:00:00Z",
    "event_type": "therapist_unavailable",
    "therapist_id": "T123",
    "therapist_name": "Dr. Sarah Johnson",
    "reason": "Emergency leave",
    "duration": "14 days",
    "affected_appointments": 15,
    "priority_calculation": "completed",
    "high_priority": 5,
    "medium_priority": 7,
    "low_priority": 3
  },
  
  "appointments": [
    {
      "appointment_id": "A001",
      "patient_id": "P999",
      "patient_name": "Maria Rodriguez",
      "original_date": "2025-11-20T10:00:00Z",
      "original_provider": "T123",
      "no_show_risk": 0.8,
      "priority_score": 87,
      "priority_level": "high",
      
      "workflow_stages": [
        {
          "stage": "filtering",
          "timestamp": "2025-11-15T09:05:23Z",
          "duration_seconds": 12,
          "candidates_initial": 8,
          "candidates_qualified": 3,
          "filters_applied": [
            {"name": "skills", "passed": 6, "failed": 2},
            {"name": "license", "passed": 6, "failed": 0},
            {"name": "poc_status", "passed": 5, "failed": 1},
            {"name": "payer_rules", "passed": 5, "failed": 0},
            {"name": "location", "passed": 4, "failed": 1},
            {"name": "telehealth", "passed": 4, "failed": 0},
            {"name": "availability", "passed": 3, "failed": 1},
            {"name": "capacity", "passed": 3, "failed": 0}
          ],
          "qualified_providers": ["P001", "P004", "P006"]
        },
        {
          "stage": "scoring",
          "timestamp": "2025-11-15T09:05:35Z",
          "duration_seconds": 8,
          "scoring_model_version": "v2.1",
          "ranked_candidates": [
            {
              "provider_id": "P001",
              "provider_name": "Dr. Emily Ross",
              "total_score": 105,
              "score_breakdown": {
                "continuity": 0,
                "specialty": 35,
                "preference": 30,
                "load_balance": 20,
                "day_match": 20
              },
              "reasons": [
                "Perfect specialty match (orthopedic)",
                "Gender preference met (female)",
                "Ideal time slot match (Tuesday 10 AM)",
                "Good availability (60% capacity)"
              ]
            },
            {
              "provider_id": "P006",
              "provider_name": "Dr. Anna Park",
              "total_score": 85,
              "score_breakdown": {...}
            },
            {
              "provider_id": "P004",
              "provider_name": "Dr. Michael Lee",
              "total_score": 83,
              "score_breakdown": {...}
            }
          ]
        },
        {
          "stage": "consent",
          "timestamp": "2025-11-15T09:30:45Z",
          "duration_seconds": 2687,
          "offered_provider": {
            "provider_id": "P001",
            "provider_name": "Dr. Emily Ross"
          },
          "communication": {
            "channel": "sms",
            "preferred_channel": "sms",
            "phone_number": "+1-555-0123",
            "message_id": "MSG_20251115_093045_A001",
            "message_sent": "2025-11-15T09:30:45Z",
            "message_status": "delivered"
          },
          "patient_response": {
            "response": "YES",
            "timestamp": "2025-11-15T10:15:32Z",
            "response_time_minutes": 45
          }
        },
        {
          "stage": "booking",
          "timestamp": "2025-11-15T10:16:05Z",
          "duration_seconds": 8,
          "new_provider_id": "P001",
          "new_provider_name": "Dr. Emily Ross",
          "appointment_date": "2025-11-20T10:00:00Z",
          "same_datetime": true,
          "emr_update": {
            "status": "success",
            "update_id": "EMR_UPD_20251115_101605",
            "fields_updated": ["provider_id", "status", "last_modified"]
          },
          "notifications_sent": [
            {
              "recipient": "patient",
              "type": "sms",
              "status": "sent",
              "message": "Confirmation sent"
            },
            {
              "recipient": "provider_new",
              "type": "email",
              "status": "sent",
              "message": "New patient notification"
            },
            {
              "recipient": "front_desk",
              "type": "system_alert",
              "status": "sent",
              "message": "Successful rebook notification"
            }
          ]
        }
      ],
      
      "final_status": "BOOKED",
      "final_provider_id": "P001",
      "final_provider_name": "Dr. Emily Ross",
      "total_resolution_time_minutes": 76,
      "manual_intervention_required": false,
      "patient_satisfaction_estimated": 0.95,
      "compliance_status": "fully_compliant",
      "revenue_preserved": 120.00
    },
    
    {
      "appointment_id": "A002",
      "patient_id": "P456",
      "patient_name": "John Davis",
      "no_show_risk": 0.9,
      "priority_score": 78,
      
      "workflow_stages": [
        {"stage": "filtering", ...},
        {"stage": "scoring", ...},
        {
          "stage": "consent",
          "offers": [
            {"provider": "P004", "response": "NO"},
            {"provider": "P006", "response": "NO"},
            {"provider": "P001", "response": "TIMEOUT"}
          ],
          "all_declined": true
        },
        {
          "stage": "backfill",
          "timestamp": "2025-11-15T14:10:00Z",
          "freed_slot": {
            "date": "2025-11-18T14:00:00Z",
            "duration": 60,
            "added_to_waitlist": true
          },
          "high_risk_patients_contacted": 3,
          "slot_filled_with": {
            "patient_id": "P045",
            "patient_name": "Sarah Miller",
            "no_show_risk": 0.75,
            "time_to_fill_minutes": 292
          },
          "original_patient_reschedule": {
            "new_appointment_date": "2025-11-20T08:00:00Z",
            "provider_id": "P006",
            "provider_name": "Dr. Anna Park",
            "continuity": true,
            "availability_match": true,
            "extra_reminders_scheduled": 3
          }
        }
      ],
      
      "final_status": "RESCHEDULED",
      "final_provider_id": "P006",
      "total_resolution_time_minutes": 305,
      "manual_intervention_required": false,
      "revenue_preserved": 120.00,
      "additional_revenue_from_backfill": 120.00
    },
    
    {
      "appointment_id": "A013",
      "patient_id": "P789",
      "patient_name": "Tom Wilson",
      "no_show_risk": 0.2,
      "priority_score": 35,
      
      "workflow_stages": [
        {"stage": "filtering", "candidates_qualified": 0},
        {
          "stage": "hod_assignment",
          "timestamp": "2025-11-15T15:30:00Z",
          "reason": "No qualified providers available",
          "hod_id": "P000",
          "hod_name": "Dr. Robert Williams",
          "manual_review_flagged": true,
          "front_desk_notified": true
        }
      ],
      
      "final_status": "HOD_ASSIGNED",
      "final_provider_id": "P000",
      "manual_intervention_required": true,
      "manual_task_id": "MANUAL_A013",
      "assigned_to": "Sarah Chen"
    }
    
    // ... (remaining 12 appointments)
  ],
  
  "session_summary": {
    "total_appointments": 15,
    "outcomes": {
      "booked": 11,
      "rescheduled": 2,
      "hod_assigned": 1,
      "pending": 1
    },
    "success_rate": 0.93,
    "average_resolution_time_minutes": 87,
    "manual_interventions_required": 2,
    "revenue_preserved": 1800.00,
    "additional_revenue_from_backfill": 240.00,
    "total_revenue_impact": 2040.00,
    "slots_prevented_from_going_empty": 2,
    "patient_satisfaction_avg": 0.89,
    "compliance_violations": 0,
    "high_no_show_patients_helped": 3
  },
  
  "performance_metrics": {
    "agent_execution_times": {
      "matching_agent_avg_ms": 8200,
      "consent_agent_avg_ms": 180000,
      "backfill_agent_avg_ms": 15000
    },
    "mcp_server_calls": {
      "knowledge_server": 45,
      "domain_api_server": 312
    },
    "llm_calls": {
      "total": 18,
      "tokens_used": 145000,
      "cost_usd": 2.10
    }
  },
  
  "compliance_audit": {
    "poc_validations": 15,
    "poc_violations": 0,
    "payer_rule_checks": 15,
    "payer_rule_violations": 0,
    "consent_captured": 13,
    "consent_pending": 1,
    "consent_timeout": 1,
    "hipaa_compliant": true
  }
}
```

3. Update all appointments in EMR:
   ```
   EMR Batch Update:
   - 11 appointments: Status → CONFIRMED (new provider assigned)
   - 2 appointments: Status → RESCHEDULED (new date/time)
   - 1 appointment: Status → PENDING_HOD (manual review)
   - 1 appointment: Status → PENDING_CONSENT (awaiting patient)
   
   All updates: Timestamped, logged, auditable
   ```

4. Generate and distribute reports:

**Report 1: Sarah (Front Desk) - Action Items**

   ```
   Manual Tasks:
   - A013: Call Tom Wilson (no provider match, assigned to HOD)
     Priority: Medium, Due: Within 24h
   - A015: Follow up with Linda Chen (consent pending, call if no response by EOD)
     Priority: Low, Due: EOD today
   ```

**Report 2: Dr. Williams (HOD) - Review Queue**

   ```
   Assigned to You:
   - A013: Tom Wilson (Mon 11/25 3 PM)
     Reason: No qualified provider available for specialty requirement
     Action: Review case, consider referral to specialist
   ```

**Report 3: Management - Session Summary**

   ```
   Session Performance:
   - Total processed: 15 appointments in 7h 45m
   - Success rate: 93% (14/15 resolved)
   - Revenue preserved: $2,040
   - Manual intervention: 2 cases (13%)
   - Patient satisfaction: 89% estimated
   - Compliance: 100% (zero violations)
   ```

5. Archive audit log:
   ```
   Storage:
   - Primary: Database (searchable, indexed by appointment_id, patient_id, date)
   - Backup: JSON file in audit_logs/2025-11-15/SESSION_090000.json
   - Retention: 7 years (HIPAA requirement)
   - Access: Restricted (admin, compliance, management only)
   ```


**Output:**

```
Reconciliation Complete:
✓ All 15 appointments processed
✓ EMR updated (15/15)
✓ Audit log generated and archived
✓ Stakeholders notified (patients, providers, staff)
✓ Reports distributed
✓ Manual tasks assigned (2)
✓ Compliance verified (0 violations)
✓ Revenue impact calculated (+$2,040)

Session ID: SESSION_2025-11-15_090000
Audit Log: audit_logs/2025-11-15/SESSION_090000.json
Status: COMPLETE
```

**Success Criteria:**

- All appointments have final status
- EMR is up-to-date
- Complete audit trail exists
- All stakeholders notified
- Manual tasks assigned where needed
- Compliance verified
- No ambiguity in final state

**Knowledge Required:**

- Audit log format standards (config)
- Report templates (knowledge doc)
- Data retention policies (compliance doc)
- Stakeholder notification rules (knowledge doc)

---

## Updated Architecture

```
CLI Interface (Demo)
    ↓
LangGraph Orchestrator + Claude
- Reads PDF knowledge for ALL rules
- Orchestrates 6-stage workflow
- Emits events for A2A
    ↓
Event Queue (Python → Redis later)
    ↓
┌──────────────┬──────────────┬──────────────┐
↓              ↓              ↓              ↓
Trigger        Matching       Consent        Backfill
Handler        Agent          Agent          Agent
(Priority      (8 filters +   (Multi-        (Waitlist +
Scoring)       5 scoring)     channel)       No-show)
    ↓              ↓              ↓              ↓
┌────────────────┴──────────────┴──────────────┘
↓
┌──────────────┬──────────────┐
↓              ↓
Knowledge MCP  Domain API MCP
- Matching     - Provider API (license, skills, capacity)
  rules        - Patient API (preferences, history, POC)
- Scoring      - Appointment API (schedule, update)
  weights      - Notification API (SMS, email, IVR)
- Payer rules  - Waitlist API (add, query, fill)
- POC policies
- Workflow
  steps
```

## Updated Project Structure

```
therapist-replacement-poc/
├── config/
│   ├── llm_config.yaml
│   ├── mcp_servers.yaml
│   ├── scoring_weights.yaml         # NEW: Scoring factor weights
│   ├── payer_rules.yaml             # NEW: Insurance/payer compliance
│   └── reminder_policies.yaml       # NEW: Reminder frequency by risk
│
├── interfaces/
│   ├── llm_provider.py
│   ├── workflow_engine.py
│   ├── event_bus.py
│   └── risk_calculator.py           # NEW: No-show risk interface
│
├── adapters/
│   ├── llm/ (anthropic, openai, ollama)
│   ├── workflow/ (langgraph, custom)
│   └── events/ (memory_queue, redis)
│
├── mcp_servers/
│   ├── knowledge/
│   │   ├── server.py
│   │   └── pdf_parser.py
│   └── domain_api/
│       ├── server.py
│       ├── mock_backends.py
│       ├── provider_api.py          # NEW: Provider details
│       ├── patient_api.py           # NEW: Patient details
│       ├── appointment_api.py       # NEW: Scheduling
│       ├── notification_api.py      # NEW: Multi-channel
│       └── waitlist_api.py          # NEW: Waitlist management
│
├── agents/
│   ├── trigger_handler.py           # NEW: Priority scoring
│   ├── matching_agent.py            # ENHANCED: 8 filters + 5 scoring
│   ├── consent_agent.py             # ENHANCED: Multi-channel
│   └── backfill_agent.py            # ENHANCED: No-show targeting
│
├── orchestrator/
│   ├── workflow.py                  # ENHANCED: 6-stage workflow
│   ├── event_handler.py
│   └── mcp_client.py
│
├── knowledge/
│   ├── matching_rules.md            # ENHANCED: 8 filter rules
│   ├── scoring_weights.md           # NEW: 5-factor scoring
│   ├── payer_rules.md               # NEW: Insurance compliance
│   ├── poc_policies.md              # NEW: Plan of Care rules
│   ├── communication_policies.md    # NEW: Multi-channel rules
│   ├── no_show_risk_model.md        # NEW: Risk calculation
│   ├── waitlist_policies.md         # NEW: Backfill rules
│   └── workflow_steps.md            # ENHANCED: 6-stage flow
│
├── demo/
│   ├── cli.py                       # ENHANCED: All 6 stages
│   ├── test_data.py                 # ENHANCED: Complete profiles
│   ├── scenarios.py                 # ENHANCED: All use cases
│   └── personas.py                  # NEW: 5 personas with stories
│
├── tests/
│   ├── test_trigger.py              # NEW: Priority scoring tests
│   ├── test_filtering.py            # NEW: 8 filter tests
│   ├── test_scoring.py              # NEW: 5-factor scoring tests
│   ├── test_consent.py              # NEW: Multi-channel tests
│   ├── test_backfill.py             # NEW: Waitlist tests
│   └── test_workflow_e2e.py         # ENHANCED: Full 6-stage
│
├── audit_logs/                      # NEW: Audit trail storage
├── requirements.txt
├── README.md
└── .env.example
```

## Implementation Phases (Updated - 2 Weeks)

### Week 1: Core Infrastructure + Complete Data Models

#### Day 1-2: Foundation + All Interfaces

- Project structure setup
- ALL interfaces (LLM, Workflow, Event, Risk Calculator)
- Anthropic adapter
- Event queue (in-memory)
- Complete configuration system
- **NEW**: Patient/Provider data models with full attributes
- **NEW**: No-show risk calculation interface

Files:

- All interface files
- Complete data models (Patient, Provider, Appointment with all fields)
- Risk calculation formulas

#### Day 3-4: MCP Servers (Complete)

- Knowledge MCP Server (PDF + markdown parsing)
- Domain API MCP Server with ALL endpoints:
                                                                                                                                - Provider API: get_provider, list_providers, check_skills, check_license, check_capacity, check_availability
                                                                                                                                - Patient API: get_patient, get_preferences, get_history, get_no_show_risk, get_poc_status, get_communication_prefs
                                                                                                                                - Appointment API: get_appointment, update_appointment, create_appointment, cancel_appointment
                                                                                                                                - Notification API: send_sms, send_email, send_ivr, check_delivery_status
                                                                                                                                - Waitlist API: add_to_waitlist, query_waitlist, fill_slot, remove_from_waitlist
- Mock data with realistic values for all fields
- Test all MCP endpoints

Files:

- `mcp_servers/knowledge/server.py`
- `mcp_servers/domain_api/server.py`
- 5 API modules (provider, patient, appointment, notification, waitlist)
- Comprehensive mock data

#### Day 5: ALL Agent Logic

- **Trigger Handler**: Priority scoring (no-show + POC + revenue + satisfaction)
- **Matching Agent**: 
                                                                                                                                - 8 filter functions (skills, license, POC, payer, location, telehealth, availability, capacity)
                                                                                                                                - 5 scoring functions (continuity, specialty, preference, load, day match)
                                                                                                                                - Ranking logic
- **Consent Agent**: 
                                                                                                                                - Multi-channel selection (SMS/Email/IVR)
                                                                                                                                - Response handling (YES/NO/INFO/TIMEOUT)
                                                                                                                                - Retry logic
- **Backfill Agent**: 
                                                                                                                                - Waitlist management
                                                                                                                                - High no-show risk targeting
                                                                                                                                - Availability window matching
                                                                                                                                - HOD assignment fallback

Files:

- `agents/trigger_handler.py`
- `agents/matching_agent.py` (comprehensive)
- `agents/consent_agent.py` (multi-channel)
- `agents/backfill_agent.py` (complete backfill logic)

### Week 2: Orchestration + Knowledge + Demo

#### Day 6-7: LangGraph Workflow (6 Stages)

- Design state machine with 6 nodes:

                                                                                                                                1. Trigger Node (priority scoring)
                                                                                                                                2. Filtering Node (8 filters)
                                                                                                                                3. Scoring Node (5 factors)
                                                                                                                                4. Consent Node (multi-channel)
                                                                                                                                5. Backfill Node (waitlist + reschedule)
                                                                                                                                6. Reconciliation Node (audit logging)

- Conditional edges based on outcomes
- Event emission at each stage
- Error handling and retry logic
- Integration with MCP servers

Files:

- `orchestrator/workflow.py` (complete 6-stage graph)
- `adapters/workflow/langgraph_adapter.py`
- `orchestrator/event_handler.py`

#### Day 8-9: ALL Knowledge Documents

- **matching_rules.md**: 8 filter rules with criteria
- **scoring_weights.md**: 5-factor scoring model
- **payer_rules.md**: Medicare, PPO, HMO, Workers Comp rules
- **poc_policies.md**: Plan of Care validation rules
- **communication_policies.md**: SMS/Email/IVR selection logic
- **no_show_risk_model.md**: Risk calculation formula
- **waitlist_policies.md**: Backfill prioritization rules
- **workflow_steps.md**: Complete 6-stage workflow description
- Convert critical docs to PDF for demo

Files:

- 8 knowledge markdown files (comprehensive)
- PDF versions of key docs

#### Day 10: CLI Demo + Complete Test Data

- Interactive CLI with all 6 stages visible
- Commands: "therapist departed [ID]", "show audit [session]", "show metrics"
- Real-time stage display with progress indicators
- Comprehensive test data:
                                                                                                                                - 15 appointments (varied priority levels)
                                                                                                                                - 8 providers (varied skills, capacities, availabilities)
                                                                                                                                - 5 personas (Maria, John, Sarah M., Tom, Linda)
                                                                                                                                - Complete patient histories
                                                                                                                                - No-show risk scores for all patients
                                                                                                                                - POC statuses
                                                                                                                                - Communication preferences
- Demo scenarios covering all use cases:

                                                                                                                                1. Perfect match (Maria → Dr. Ross)
                                                                                                                                2. High no-show backfill (John → waitlist → reschedule)
                                                                                                                                3. HOD assignment (Tom → no match)
                                                                                                                                4. Multi-channel consent (different patient preferences)
                                                                                                                                5. Continuity priority (patient seen provider before)
                                                                                                                                6. Complex scoring (multiple factors)

Files:

- `demo/cli.py` (full 6-stage display)
- `demo/test_data.py` (comprehensive data)
- `demo/scenarios.py` (all 6 use cases)
- `demo/personas.py` (5 personas with stories)

#### Day 11-12: Testing + Documentation

- Unit tests for ALL components:
                                                                                                                                - Trigger handler (priority scoring)
                                                                                                                                - Each of 8 filters
                                                                                                                                - Each of 5 scoring factors
                                                                                                                                - Multi-channel consent
                                                                                                                                - Waitlist logic
                                                                                                                                - HOD assignment
- Integration tests:
                                                                                                                                - Full 6-stage workflow
                                                                                                                                - All use cases end-to-end
                                                                                                                                - Error scenarios
                                                                                                                                - Timeout handling
- Documentation:
                                                                                                                                - README with complete setup
                                                                                                                                - Architecture diagrams (all 6 stages)
                                                                                                                                - API documentation (all MCP endpoints)
                                                                                                                                - Knowledge document index
                                                                                                                                - Persona stories
                                                                                                                                - Use case validation matrix
                                                                                                                                - Extension guide (how to add new workflows)

Files:

- 6 test files (one per major component)
- `test_workflow_e2e.py` (all 6 use cases)
- Complete README
- Architecture diagrams

## Success Criteria (Comprehensive)

### Use Case Coverage:

1. ✅ Trigger: Priority scoring with no-show risk
2. ✅ Filtering: All 8 filters implemented
3. ✅ Scoring: All 5 factors implemented
4. ✅ Consent: Multi-channel (SMS/Email/IVR)
5. ✅ Backfill: Waitlist + no-show targeting + HOD fallback
6. ✅ Audit: Complete reconciliation and logging

### Functional Requirements:

- ✅ CLI demo runs all 15 appointments
- ✅ All 6 stages execute correctly
- ✅ Dynamic workflow (change knowledge → behavior changes)
- ✅ MCP servers expose all APIs
- ✅ Vendor swap (LLM provider) works
- ✅ Backend swap (mock → real) works
- ✅ Complete audit trail generated
- ✅ All personas validated

### Quality Requirements:

- ✅ >80% test coverage
- ✅ All use cases pass end-to-end tests
- ✅ Documentation covers all features
- ✅ Setup completes in <15 minutes
- ✅ Demo runs without errors
- ✅ Audit log is human-readable
- ✅ Extensible architecture demonstrated

## Deliverables (Comprehensive)

1. **Working System**:

                                                                                                                                                                                                - CLI demo application (all 6 stages)
                                                                                                                                                                                                - 2 MCP servers (Knowledge + Domain API with 5 APIs)
                                                                                                                                                                                                - 4 agents (Trigger, Matching, Consent, Backfill)
                                                                                                                                                                                                - LangGraph orchestrator (6-stage workflow)
                                                                                                                                                                                                - Event bus with A2A communication

2. **Knowledge Base**:

                                                                                                                                                                                                - 8 knowledge documents (markdown + PDF)
                                                                                                                                                                                                - All matching rules documented
                                                                                                                                                                                                - All scoring weights documented
                                                                                                                                                                                                - Payer rules documented
                                                                                                                                                                                                - POC policies documented

3. **Test Suite**:

                                                                                                                                                                                                - Unit tests (all components)
                                                                                                                                                                                                - Integration tests (6 use cases)
                                                                                                                                                                                                - Demo scenarios (15 appointments)
                                                                                                                                                                                                - Persona validation tests

4. **Documentation**:

                                                                                                                                                                                                - README with architecture
                                                                                                                                                                                                - Setup guide (<15 min)
                                                                                                                                                                                                - API documentation (all MCP endpoints)
                                                                                                                                                                                                - Persona stories
                                                                                                                                                                                                - Use case mapping
                                                                                                                                                                                                - Extension guide

5. **Demonstration Materials**:

                                                                                                                                                                                                - CLI demo script
                                                                                                                                                                                                - Sample output showing all 6 stages
                                                                                                                                                                                                - Audit log example
                                                                                                                                                                                                - Metrics dashboard mockup

## Post-Demo Extension Points

- Add web UI (FastAPI + React)
- Real-time dashboard (metrics, alerts)
- Upgrade to Redis for production scale
- Add more LLM adapters (OpenAI, Gemini, local)
- Connect to real WebPT/Athena API
- Add more workflows (cancellations, waitlist optimization)
- Deploy as microservices (Docker/K8s)
- Add machine learning for no-show prediction
- Integrate with actual EMR systems
- Add compliance reporting tools

### To-dos

- [ ] Set up project structure, create vendor-agnostic interfaces (LLM, Event Bus, Workflow), implement Anthropic adapter, configure YAML-based settings
- [ ] Build Knowledge MCP Server (PDF parsing, resource retrieval) and Domain API MCP Server (mock Provider, Patient, Appointment, Notification APIs)
- [ ] Implement three agents: Matching Agent (scoring with 6 rules), Consent Agent (patient communication), Backfill Agent (HOD assignment fallback)
- [ ] Build LangGraph workflow with state machine, integrate event bus for A2A communication, connect to MCP servers
- [ ] Write matching rules document (6 priority rules), workflow definition, compliance rules in markdown/PDF format
- [ ] Create interactive CLI with realistic test data (15 appointments, 8 providers), implement 4 demo scenarios showing different matching cases
- [ ] Write unit tests for agents, integration tests for workflow, create README with setup instructions and architecture diagrams