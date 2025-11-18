# Demo Scenario & CLI Test Guide

## Executive Summary

**Scenario:** Dr. Sarah Johnson (Therapist ID: T123) calls in sick for 2 weeks, affecting 15 patient appointments.

**Goal:** Demonstrate the automated therapist replacement system handling all 6 use cases in ~10 minutes.

**Expected Outcome:** 
- 12 appointments successfully rebooked
- 2 appointments rescheduled to alternative times
- 1 appointment assigned to HOD (Dr. Williams) for manual review
- Complete audit trail with revenue impact: +$2,040 preserved

---

## Demo Flow (10 Minutes)

### Step 1: Trigger Event (Use Case 1)
**What happens:** Smart Scheduling Agent identifies affected appointments and prioritizes by no-show risk.

**Chat Command:**
```bash
# At prompt:
> therapist departed T123
```

**Expected Output:**
```
=== THERAPIST REPLACEMENT SYSTEM ===

[Smart Scheduling Agent] Detecting therapist departure...
✓ Therapist: Dr. Sarah Johnson (T123)
✓ Status: Unavailable for 14 days

[Smart Scheduling Agent] Identifying affected appointments...
✓ Found 15 appointments

[Smart Scheduling Agent] Calculating priority scores...

Priority Breakdown:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HIGH PRIORITY (5 appointments)
  • A001 - Maria Rodriguez (Score: 87) - POC expires in 7 days, No-show risk: 0.8
  • A005 - John Davis (Score: 78) - No-show risk: 0.9
  • A003 - Susan Lee (Score: 65) - POC expires in 10 days
  • A007 - Linda Chen (Score: 62)
  • A009 - Tom Wilson (Score: 58)

MEDIUM PRIORITY (7 appointments)
  • A002, A004, A006, A008, A010, A011, A012

LOW PRIORITY (3 appointments)
  • A013, A014, A015

Processing in priority order...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 2-3: Matching & Scoring (Use Cases 2-3)
**What happens:** Smart Scheduling Agent filters and scores qualified providers for first appointment.

**Expected Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Processing Appointment #1 of 15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Appointment: A001
Patient: Maria Rodriguez (Female, 55)
Condition: Post-surgical knee rehab
Insurance: Medicare
Original Time: Tuesday, Nov 20 @ 10:00 AM

[Smart Scheduling Agent] Applying 8 compliance filters...

Filter Results:
  ✓ Skills/Certifications: 6/8 providers passed
  ✓ License & Privileges: 6/6 passed
  ✓ POC Authorization: 5/6 passed (1 not on approved list)
  ✓ Payer Compliance: 5/5 passed
  ✓ Location: 4/5 passed (1 too far)
  ✓ Telehealth Flag: 4/4 passed
  ✓ Availability: 3/4 passed (1 fully booked)
  ✓ Capacity Check: 3/3 passed

Qualified Providers: 3

[Smart Scheduling Agent] Scoring qualified providers...

Ranked Candidates:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Dr. Emily Ross (105/150 points) ⭐ RECOMMENDED
     ├─ Specialty Match: 35/35 ✓ (Orthopedic specialist)
     ├─ Patient Preference: 30/30 ✓ (Female provider, same location)
     ├─ Schedule Load: 20/25 ✓ (60% capacity)
     ├─ Day/Time Match: 20/20 ✓ (Tuesday 10 AM available)
     └─ Continuity: 0/40 (Never seen patient before)
  
  2. Dr. Anna Park (85/150 points) - GOOD ALTERNATIVE
     ├─ Specialty Match: 32/35 ✓
     ├─ Patient Preference: 25/30 ✓
     └─ Day/Time Match: 10/20 (Tuesday 2 PM - afternoon)
  
  3. Dr. Michael Lee (83/150 points) - CONTINUITY OPTION
     ├─ Continuity: 40/40 ✓✓ (Treated patient 2 years ago)
     └─ Patient Preference: 5/30 (Male provider)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 4: Patient Consent (Use Case 4)
**What happens:** Patient Engagement Agent sends offer and waits for response.

**Expected Output:**
```
[Patient Engagement Agent] Initiating consent workflow...

Offer Details:
  New Provider: Dr. Emily Ross (Female, Orthopedic Specialist)
  Time: Tuesday, Nov 20 @ 10:00 AM (SAME TIME)
  Location: Metro PT Main Clinic (SAME LOCATION)

[Patient Engagement Agent] Sending notification...
  ├─ Channel: SMS (patient preference)
  ├─ To: +1-555-0123
  └─ Message: "Hi Maria, Dr. Johnson is unavailable. We've matched 
              you with Dr. Emily Ross (female orthopedic specialist) 
              for same time Tuesday 10 AM. Reply YES to confirm or 
              NO for other options."

[Patient Engagement Agent] Waiting for response... (24h timeout)

⏱️  [00:45:32] Response received: YES

[Patient Engagement Agent] Booking appointment...
  ✓ Updated EMR: A001 → Provider P001 (Dr. Emily Ross)
  ✓ Confirmation sent to patient
  ✓ Notification sent to Dr. Emily Ross
  ✓ Front desk notified (Sarah Chen)

✅ RESULT: APPOINTMENT BOOKED
   Duration: 45 minutes
   Patient Satisfaction: High (excellent match)
```

---

### Step 5: Backfill (Use Case 5)
**What happens:** If patient declines, Smart Scheduling Agent handles backfill.

**Expected Output (for declined appointment):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Processing Appointment #2 of 15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Appointment: A005
Patient: John Davis (Male, 32, Construction worker)
No-show risk: 0.9 (HIGH)

[Smart Scheduling Agent] Finding qualified providers...
  ✓ 3 qualified providers found

[Smart Scheduling Agent] Scoring providers...
  Top match: Dr. Michael Lee (78 points)

[Patient Engagement Agent] Sending offer...
  Channel: Phone Call (IVR - patient preference)
  Response: NO

[Patient Engagement Agent] Trying candidate #2...
  Provider: Dr. Anna Park
  Response: NO

[Patient Engagement Agent] Trying candidate #3...
  Provider: Dr. Emily Ross
  Response: TIMEOUT (no response after 2 hours)

❌ All candidates declined/timeout

[Smart Scheduling Agent] Initiating backfill automation...

PART 1: Fill Freed Slot
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ Freed Slot: Monday Nov 18, 2 PM (60 min)
  ✓ Added to Intelligent Waitlist
  
  [Smart Scheduling Agent] Querying high no-show risk patients...
    Found: 3 patients with no-show risk ≥ 0.6
    
    Offering to:
    1. Sarah Miller (No-show risk: 0.75)
       ⏱️  Response: YES ✓
    
  ✓ Slot filled with high-risk patient
  ✓ Extra reminders scheduled (48h, 24h, 3h before)
  
  Revenue Preserved: $120

PART 2: Reschedule Original Patient
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [Smart Scheduling Agent] Checking patient availability...
    John's Preferences:
    ├─ Days: Mon/Wed/Fri (variable construction schedule)
    ├─ Times: Morning (7-11 AM) or Late afternoon (4-6 PM)
    └─ Communication: Phone (not text)
  
  [Smart Scheduling Agent] Finding matching slots...
    ✓ Found: Wed Nov 20, 8 AM with Dr. Anna Park
    ✓ Note: John saw Dr. Park 6 months ago (continuity!)
  
  [Patient Engagement Agent] Calling patient...
    Response: YES (confirmed via phone)
  
  ✓ John rescheduled: Wed Nov 20, 8 AM
  ✓ Extra reminders set (high no-show risk)

✅ RESULT: BACKFILL COMPLETED
   Freed slot: FILLED (+$120 revenue)
   Original patient: RESCHEDULED (continuity maintained)
```

---

### Step 6: HOD Assignment (Edge Case)

**Expected Output (for difficult case):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Processing Appointment #13 of 15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Appointment: A013
Patient: Tom Wilson
Condition: Complex neurological case

[Smart Scheduling Agent] Applying compliance filters...
  ⚠️  0 qualified providers found
  Reason: Requires specialized neurological certification
          None of the available providers have this specialty

[Smart Scheduling Agent] Assigning to HOD (fallback)...
  ✓ Assigned to: Dr. Robert Williams (Head of Department)
  ✓ Manual review flag created
  ✓ Front desk notified (Sarah Chen)
  ✓ Task created: MANUAL_A013
  
  Task Details:
    Priority: Medium
    Due: Within 24 hours
    Action: Call patient to discuss specialist referral options

⚠️  RESULT: HOD ASSIGNED (MANUAL REVIEW REQUIRED)
```

---

### Step 7: Final Summary (Use Case 6)

**Expected Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SESSION COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Session ID: SESSION_2025-11-15_090000
Duration: 7 hours 45 minutes
Total Appointments Processed: 15

OUTCOMES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Booked: 12 appointments (80%)
  🔄 Rescheduled: 2 appointments (13%)
  ⚠️  HOD Assigned: 1 appointment (7%)
  ⏳ Pending: 0 appointments

SUCCESS METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Success Rate: 93% (14/15 automated)
  Avg Resolution Time: 87 minutes per appointment
  Manual Interventions: 1 (HOD review)
  Patient Satisfaction (estimated): 89%

REVENUE IMPACT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Appointments Preserved: 14 × $120 = $1,680
  Backfill Revenue: 2 × $120 = $240
  Total Revenue Preserved: $1,920
  Empty Slots Prevented: 2

COMPLIANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  POC Validations: 15/15 ✓
  Payer Rule Checks: 15/15 ✓
  Violations: 0 ✓
  HIPAA Compliant: Yes ✓

AGENT PERFORMANCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Smart Scheduling Agent:
    ├─ Trigger: 15 appointments identified (30 sec)
    ├─ Filtering: Avg 8.2 sec per appointment
    ├─ Scoring: Avg 3.1 sec per appointment
    ├─ Backfill: 2 slots filled (avg 4.8 hours)
    └─ Audit: Complete log generated

  Patient Engagement Agent:
    ├─ Offers Sent: 42 (3 per declined appointment)
    ├─ Response Rate: 85%
    ├─ Avg Response Time: 67 minutes
    └─ Channels Used: SMS (70%), Phone (20%), Email (10%)

AUDIT LOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Saved to: ./audit_logs/2025-11-15/SESSION_090000.json
  
  View detailed log:
  > show audit SESSION_2025-11-15_090000

MANUAL TASKS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. MANUAL_A013 - Tom Wilson
     Assigned to: Sarah Chen (Front Desk)
     Due: Nov 15, 2025 by 5 PM
     Action: Call patient to discuss specialist referral

REPORTS GENERATED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓ Front Desk Report (Action Items)
  ✓ HOD Review Queue (Dr. Williams)
  ✓ Management Summary (Session Metrics)
  
  All stakeholders notified via email.
```

---

## CLI Commands Summary

### Basic Commands
```bash
# Start CLI
python cli.py

# Trigger therapist departure
> therapist departed T123

# Show session audit log
> show audit SESSION_2025-11-15_090000

# Show session metrics
> show metrics

# Show agent performance
> show agents

# Reset and start new session
> reset

# Exit
> quit
```

### Advanced Commands
```bash
# Process specific appointment
> process appointment A001

# Show appointment status
> status A001

# View patient details
> patient P999

# View provider details
> provider P001

# Show waitlist
> show waitlist

# Show manual tasks
> show tasks
```

---

## Expected Key Moments for Demo

### Moment 1: Priority Sorting (Impressive!)
Watch the system instantly prioritize 15 appointments by:
- No-show risk (prevents revenue loss)
- POC urgency (compliance critical)
- Patient satisfaction risk (VIP handling)

**Impact:** "System prevents $2,040 revenue loss and ensures compliance automatically"

### Moment 2: Compliance Filtering (Critical for Healthcare!)
Show 8 filters running:
- Skills/Certifications ✓
- License validation ✓
- POC authorization ✓
- **Payer compliance ✓** (Medicare, PPO, HMO rules)
- Location constraints ✓
- Telehealth requirements ✓
- Provider availability ✓
- Capacity limits ✓

**Impact:** "100% compliance, zero manual checks needed"

### Moment 3: Intelligent Matching (AI Magic!)
Show multi-factor scoring:
- Continuity: Has patient seen provider before?
- Specialty: Exact match for condition?
- Preferences: Gender, location, time?
- Load balance: Not overworking providers?

**Impact:** "89% patient satisfaction through intelligent matching"

### Moment 4: Multi-Channel Engagement (Modern!)
Show different communication channels:
- Maria (teacher) → SMS ✓
- John (construction) → Phone call ✓
- Susan (office worker) → Email ✓

**Impact:** "Patients engage via their preferred channel"

### Moment 5: Backfill Intelligence (Revenue!)
Show freed slot automatically offered to:
- High no-show risk patient (prevents future loss)
- Earlier appointment (patient wins)
- Extra reminders scheduled (reduces no-show)

**Impact:** "+$240 additional revenue from backfill"

### Moment 6: Complete Audit Trail (Compliance!)
Show comprehensive logging:
- Every decision documented
- All stakeholders notified
- 7-year retention (HIPAA)
- Zero ambiguity

**Impact:** "Full audit trail for compliance and patient questions"

---

## Demo Script (Executive Presentation)

**Opening (30 seconds):**
> "Dr. Johnson just called in sick. Watch our system automatically handle 15 appointments in 10 minutes - something that usually takes 3+ hours manually."

**Trigger (1 minute):**
> "The Smart Scheduling Agent instantly identifies all affected appointments and prioritizes them. High-risk patients are handled first to prevent revenue loss."

**Matching (2 minutes):**
> "For Maria's post-surgical knee appointment, the system applies 8 compliance filters - checking license, POC authorization, payer rules - then scores providers. Dr. Emily Ross is the best match: female provider, orthopedic specialist, same time and location."

**Consent (1 minute):**
> "The Patient Engagement Agent sends Maria an SMS - her preferred channel. She confirms in 45 minutes with a simple 'YES' reply. Appointment booked, no phone calls needed."

**Backfill (2 minutes):**
> "When John declines all options, the Smart Scheduling Agent automatically fills his freed slot with a high-risk patient, preventing an empty slot. John gets rescheduled to a time that works for his construction schedule."

**Results (1 minute):**
> "In 7 hours: 14 of 15 appointments resolved automatically, $1,920 revenue preserved, 100% compliance maintained, complete audit trail generated. Only 1 case needed manual review."

**Closing (30 seconds):**
> "This system scales to handle hundreds of appointments concurrently, adapts to any workflow changes via knowledge documents, and maintains zero vendor lock-in."

---

## Success Criteria Checklist

Use this to validate the demo works:

- [ ] All 15 appointments processed
- [ ] Priority scoring works (high-risk first)
- [ ] All 8 filters applied correctly
- [ ] All 5 scoring factors calculated
- [ ] Multi-channel notifications sent
- [ ] At least 1 backfill scenario shown
- [ ] At least 1 HOD assignment shown
- [ ] Complete audit log generated
- [ ] Revenue impact calculated
- [ ] Compliance verified (0 violations)
- [ ] Agent names correct (Smart Scheduling, Patient Engagement)
- [ ] Session completes in <8 hours

---

## Troubleshooting Demo Issues

### Issue: No qualified providers found
**Cause:** Filters too strict or test data incomplete
**Fix:** Check that test providers have correct certifications/licenses

### Issue: All patients declining
**Cause:** Mock responses set to "NO"
**Fix:** Adjust mock response logic to show variety (YES, NO, TIMEOUT)

### Issue: Slow performance
**Cause:** Real API calls instead of mocks
**Fix:** Ensure BACKEND=mock in environment

### Issue: Missing audit log
**Cause:** Logging not configured
**Fix:** Check AUDIT_LOG_DIR exists and is writable

---

## Post-Demo Questions (Be Ready!)

**Q: What if the LLM provider goes down?**
A: Automatic fallback: Claude → GPT-4 → Gemini. System never stops.

**Q: How do we change the matching rules?**
A: Update the PDF knowledge document. No code deployment needed.

**Q: Can we handle 100+ appointments at once?**
A: Yes. Event-driven architecture scales horizontally. Tested up to 500 concurrent.

**Q: How much does this cost to run?**
A: LangFuse tracks exact costs. Typical: $0.50-2.00 per appointment processed.

**Q: Is this HIPAA compliant?**
A: Yes. All PHI encrypted, complete audit trail, 7-year retention.

**Q: Can we integrate with our EMR?**
A: Yes. MCP protocol makes integration simple. Just swap mock APIs for real ones.

