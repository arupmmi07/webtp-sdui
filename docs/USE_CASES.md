#Use Case

This document provides detailed mapping of all 6 use cases.

---

## Use Case 1: Trigger - Identify Affected Appointments with Priority

**Story:** Dr. Sarah Johnson calls in sick for the next 2 weeks

**Actor:** Smart Scheduling Agent

**Trigger:** Therapist status change in EMR

**Pre-conditions:**
- Dr. Sarah Johnson has 15 scheduled appointments
- Patients have varying no-show risk profiles
- Some patients have POC (Plan of Care) expiration dates approaching

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

## Use Case 2: Match Candidate Filtering with Compliance

**Story:** System filters qualified providers for Maria Rodriguez's post-surgical knee appointment

**Actor:** Smart Scheduling Agent (Match Candidate Filtering)

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

## Use Case 3: Compliance and Score Gating

**Story:** Rank the 3 qualified providers for Maria using multi-factor scoring

**Actor:** Smart Scheduling Agent (Compliance and Score Gating)

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

## Use Case 4: Automated Patient Offer Flow with Multi-Channel

**Story:** Send offer to Maria via her preferred communication channel and handle her response

**Actor:** Patient Engagement Agent (Automated Patient Offer Flow)

**Input:**
- Appointment A001
- Top candidate: Dr. Emily Ross (105 pts)
- Patient communication preference: SMS (primary), Email (backup)

**Pre-conditions:**
- Patient has valid phone number and email
- Notification service (MCP) is operational
- Consent timeout is configured (24 hours)

**Flow:**

1. Retrieve patient communication preferences from Patient API
2. Compose personalized message using patient and provider details
3. Send via Notification API (MCP) - SMS channel
4. Start timeout timer (24 hours) and listen for response

**Scenarios:**

**Scenario A: Patient responds "YES"** (happens at 10:15 AM, 45 min later)
- Book appointment via Appointment API
- Send confirmation SMS
- Notify Dr. Emily Ross
- Notify Sarah (front desk)
- Log consent with timestamp
- Emit "appointment_booked" event

**Scenario B: Patient responds "NO"** (offer next candidate)
- Log decline for Dr. Emily Ross
- Offer candidate #2 (Dr. Anna Park)
- Wait for response again (24h timeout)
- If all 3 candidates declined → Emit "consent_declined_all" event

**Scenario C: Patient responds "INFO"** (provide more details)
- Send detailed provider information
- Continue waiting for YES/NO response

**Scenario D: No response after 24h** (timeout)
- Send reminder via secondary channel (Email)
- Wait additional 12 hours
- If still no response:
  - Emit "consent_timeout" event
  - Trigger backfill workflow
  - Flag for manual follow-up

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
```

**Success Criteria:**
- Message sent via preferred channel
- Response captured within timeout
- Appointment booked in EMR
- All stakeholders notified
- Consent logged with timestamp
- Audit trail complete

**Knowledge Required:**
- Communication channel configuration
- Message templates
- Timeout policies
- Escalation rules

---

## Use Case 5: Waitlist & Backfill Automation with High No-Show Targeting

**Story:** John Davis declines all 3 providers, system backfills his slot and finds him an alternative

**Actor:** Smart Scheduling Agent (Waitlist & Backfill Automation)

**Input:**
- Appointment A002 - all 3 candidates declined by patient
- John Davis profile: High no-show risk (0.9), workers comp, flexible schedule

**Pre-conditions:**
- John's original slot is now freed: Monday 11/18 2 PM
- High no-show risk patient list is available
- John's availability windows are in system

**Flow:**

### Part 1: Fill the Freed Slot

1. Add freed slot to Intelligent Waitlist
2. Query high no-show risk patients who need similar treatment:
   - No-show risk >= 0.6
   - Condition: Lower back pain OR related
   - Current appointment: Scheduled >3 days out
   - Insurance: Active

3. Offer slot to high-risk patients (prioritized by risk score):
   - P045: Sarah Miller (no-show risk 0.75)
   - P067: Tom Anderson (no-show risk 0.65)
   - P089: Lisa Wong (no-show risk 0.70)

4. Book first patient who accepts (Sarah Miller)
5. Schedule extra reminders for high-risk patient

### Part 2: Reschedule John (Original Patient)

6. Retrieve John's availability windows:
   - Preferred: Mon/Wed/Fri
   - Time: Morning (7-11 AM) or late afternoon (4-6 PM)
   - Cannot do: Tuesday
   - Flexibility: High

7. Search for slots matching availability + qualified providers
8. Auto-propose best match via preferred channel (phone call)
9. Book John's new appointment with extra reminders

**Alternative Flow: If No Match Found for John**

10. Assign to HOD (Dr. Robert Williams)
11. Flag for manual review
12. Alert Sarah (front desk)
13. Create manual task

**Output (Success Case):**
```
Backfill Results for A002:

Part 1 - Freed Slot Filled:
- Original Patient: John Davis (declined all options)
- Freed Slot: Mon 11/18 2 PM
- Backfilled With: Sarah Miller (high no-show risk 0.75)
- Time to Fill: 4 hours 52 minutes
- Revenue Preserved: $120

Part 2 - Original Patient Rescheduled:
- Patient: John Davis
- New Appointment: Wed 11/20 8 AM with Dr. Anna Park
- Match Quality: GOOD (continuity + availability match)
- Extra Reminders: 3 scheduled

System Impact:
- Empty slots prevented: 1
- High no-show risk patients helped: 2
- Revenue impact: +$120
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
- Waitlist prioritization rules
- No-show risk thresholds
- Availability window matching logic
- HOD assignment criteria
- Reminder frequency by risk level

---

## Use Case 6: Final Appointment Reconciliation & Audit

**Story:** System confirms all actions and creates comprehensive audit trail

**Actor:** Smart Scheduling Agent (Final Appointment Reconciliation)

**Input:** All events from processing 15 appointments (A001-A015)

**Pre-conditions:**
- All workflows completed
- All stakeholder notifications sent
- All EMR updates completed

**Flow:**

1. Aggregate all event logs from entire session
2. Generate comprehensive audit log (JSON format)
3. Update all appointments in EMR
4. Generate and distribute reports:
   - Sarah (Front Desk): Action Items
   - Dr. Williams (HOD): Review Queue
   - Management: Session Summary
5. Archive audit log

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
- Audit log format standards
- Report templates
- Data retention policies
- Stakeholder notification rules

---

## Use Case Summary Matrix

| Use Case | Primary Goal | Key Metrics | Success Rate Target |
|----------|-------------|-------------|---------------------|
| 1. Trigger | Prioritize appointments | Priority accuracy, Processing time | 100% identified |
| 2. Filtering | Ensure compliance | Filter accuracy, Compliance rate | 100% compliant |
| 3. Scoring | Best clinical match | Scoring accuracy, Match quality | >85% good matches |
| 4. Consent | Patient confirmation | Response rate, Time to consent | >80% response |
| 5. Backfill | Maximize utilization | Fill rate, Revenue preserved | >70% slots filled |
| 6. Audit | Complete accountability | Audit completeness, Accuracy | 100% logged |

---

## Integration Points Between Use Cases

```
Use Case 1 (Trigger)
    ↓ Emits: trigger_detected event
Use Case 2 (Filtering)
    ↓ Emits: candidates_filtered event
Use Case 3 (Scoring)
    ↓ Emits: candidates_scored event
Use Case 4 (Consent)
    ↓ Emits: appointment_booked OR consent_declined_all
    ├─ If booked → Use Case 6 (Audit)
    └─ If declined → Use Case 5 (Backfill)
Use Case 5 (Backfill)
    ↓ Emits: backfill_completed OR manual_review_needed
Use Case 6 (Audit)
    ↓ Final: Session complete
```

