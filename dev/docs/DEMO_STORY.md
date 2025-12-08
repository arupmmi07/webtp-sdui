# 🎬 Demo Story: "Dr. Sarah's Emergency - AI to the Rescue"

> **A Real Healthcare Crisis Solved by AI**  
> *November 20, 2025 - Metro Physical Therapy*

---

## 📖 The Story

### Act 1: The Crisis (7:30 AM)

**The Phone Call:**
```
📞 Dr. Sarah Johnson calls Jessica (Receptionist)
"Jessica, I'm really sorry but I have severe flu. 
I can't come in today - maybe not for the next 3 days. 
I have 8 patients scheduled today!"
```

**Jessica's Panic:**
- 8 patients expecting appointments TODAY
- Each patient has unique needs and preferences
- Manual calling would take 2+ hours
- Risk of errors, missed patients, unhappy clients
- Need to find qualified replacement providers

**The Solution:**
```
Jessica opens the AI Calendar → Clicks "Mark Unavailable"
ONE CLICK. The AI handles everything.
```

---

## 👥 The 8 Patients (Each with a Story)

### 1. 👵 Maria Rodriguez - **HIGH PRIORITY**
- **Age:** 50, Female
- **Condition:** Post-surgical knee (recent surgery)
- **No-Show Risk:** 0.05 (very reliable)
- **Time:** 9:00 AM
- **Special Needs:** 
  - Prefers female provider (gender match important)
  - Lives in zip 12345 (close to clinic)
  - Tuesday/Thursday preference
- **Why Priority:** Recent surgery, needs continuity

### 2. 👨 John Davis - **MEDIUM PRIORITY**
- **Age:** 45, Male
- **Condition:** Lower back pain (chronic)
- **No-Show Risk:** 0.15 (occasionally misses)
- **Time:** 9:30 AM
- **Special Needs:**
  - No gender preference (flexible)
  - Lives in zip 12342 (different area)
  - Monday/Wednesday/Friday preference
- **Why Priority:** Chronic condition, moderate risk

### 3. 👵 Susan Lee - **HIGH PRIORITY**
- **Age:** 62, Female
- **Condition:** Hip replacement recovery
- **No-Show Risk:** 0.03 (extremely reliable)
- **Time:** 10:00 AM
- **Special Needs:**
  - Prefers female provider
  - Lives in zip 12350 (willing to travel 15 miles)
  - Tuesday/Thursday preference
- **Why Priority:** Major surgery recovery, very compliant

### 4. 👨 Robert Chen - **MEDIUM PRIORITY**
- **Age:** 55, Male
- **Condition:** Chronic shoulder pain
- **No-Show Risk:** 0.08 (reliable)
- **Time:** 10:30 AM
- **Special Needs:**
  - No gender preference
  - Lives in zip 12347
  - Aetna insurance
  - Tuesday/Thursday/Friday preference
- **Why Priority:** Chronic pain management

### 5. 👴 David Miller - **⚠️ HIGH RISK - HOD REVIEW**
- **Age:** 58, Male
- **Condition:** Knee arthritis
- **No-Show Risk:** 0.35 (HIGH - frequently misses)
- **Time:** 2:00 PM
- **Special Needs:**
  - No preferences
  - Lives in zip 12355 (far away)
  - Medicare insurance
  - Willing to travel 12 miles
- **Why HOD Review:** High no-show risk + far location = poor match score

### 6. 👩 Lisa Brown - **LOW PRIORITY (Different Specialty)**
- **Age:** 42, Female
- **Condition:** Tennis elbow (Sports Medicine)
- **No-Show Risk:** 0.02 (very reliable)
- **Time:** 2:30 PM
- **Special Needs:**
  - Prefers female provider
  - Sports Medicine specialty needed
  - Lives in zip 12348
- **Why Low Priority:** Different specialty (not orthopedic)

### 7. 👵 Patricia Anderson - **CONTINUITY CANDIDATE**
- **Age:** 68, Female
- **Condition:** Ankle sprain recovery
- **No-Show Risk:** 0.08 (reliable)
- **Time:** 3:00 PM
- **Special Needs:**
  - **Prefers MALE provider** (unique!)
  - Has seen Dr. Michael Lee before
  - Lives in zip 12345
  - Tuesday/Thursday preference
- **Why Special:** Gender preference for male + prior history

### 8. 👨 James Wilson Jr - **NEW PATIENT**
- **Age:** 35, Male
- **Condition:** Rotator cuff injury (Sports Medicine)
- **No-Show Risk:** 0.12 (moderate)
- **Time:** 3:30 PM
- **Special Needs:**
  - No preferences (very flexible)
  - Sports Medicine needed
  - Lives in zip 12342
  - No prior provider relationship
- **Why Interesting:** New patient, very flexible, young

---

## 🤖 The AI Solution - How It Works

### Step 1: TRIGGER & PRIORITIZE (UC1)
```
✅ System detects: Dr. Sarah Johnson unavailable
✅ Identifies: 8 affected appointments
✅ Calculates priority scores:
   1. Maria (87 pts) - Post-surgical, reliable, urgent
   2. Susan (85 pts) - Hip replacement, very reliable
   3. Robert (72 pts) - Chronic pain, Aetna
   4. John (68 pts) - Chronic back, moderate risk
   5. Patricia (65 pts) - Ankle recovery, prior history
   6. James (58 pts) - New patient, flexible
   7. Lisa (52 pts) - Tennis elbow, different specialty
   8. David (45 pts) - HIGH RISK, far location
```

### Step 2: FILTER CANDIDATES (UC2)
```
Available Providers: 3 (excluding Dr. Sarah)

✅ Dr. Emily Ross (P001)
   • Orthopedic PT ✓
   • Sports PT ✓
   • Female ✓
   • 10 years experience
   • Zip 12345 (same location)
   • Available slots: TODAY

✅ Dr. James Wilson (P002)
   • Acupuncture PT
   • Manual Therapy ✓
   • Male ✓
   • 12 years experience
   • Zip 12345
   • Available slots: TODAY

✅ Dr. Michael Lee (P004) - UNAVAILABLE TODAY
   • Geriatric PT
   • Male ✓
   • 8 years experience
   • Currently unavailable (for demo contrast)
```

### Step 3: SMART SCORING (UC3) - 165 Points System
```
For Maria Rodriguez → Dr. Emily Ross:
  🏥 Specialty Match: +35 (Orthopedic ✓)
  👥 Gender Preference: +15 (Female ✓)
  📍 Location Match: +15 (Same zip)
  📊 Provider Load: +20 (Not overloaded)
  🎓 Experience Match: +20 (Similar to Sarah)
  ⏰ Time Slot: +15 (Same time available)
  📅 Day Preference: +10 (Tuesday ✓)
  ────────────────────────────────────
  ⭐ TOTAL: 130/165 = EXCELLENT MATCH

For David Miller → Dr. Emily Ross:
  🏥 Specialty: +20 (General PT, not exact)
  👥 Gender: 0 (No preference)
  📍 Location: 0 (12 miles away - outside max)
  📊 Load: +15
  🎓 Experience: +15
  ⏰ Time: +10
  📅 Day: 0 (Not preferred day)
  ────────────────────────────────────
  ⭐ TOTAL: 60/165 = NEEDS HOD REVIEW
```

### Step 4: PATIENT ENGAGEMENT (UC4)
```
✉️ Email sent to Maria:
─────────────────────────────────────────
Subject: Important: Appointment Change - Dr. Sarah Johnson

Hi Maria Rodriguez,

We wanted to reach out about your appointment TODAY at 9:00 AM.

Due to an unexpected absence, Dr. Sarah Johnson is unavailable.

We'd like to offer you:
👨‍⚕️ Dr. Emily Ross
🏥 Orthopedic Physical Therapy Specialist
📅 TODAY, November 20 at 9:00 AM
📍 Metro PT Downtown

Dr. Ross is highly qualified and available:
✓ 10 years experience
✓ Orthopedic specialist (perfect match!)
✓ Same location and time
✓ Match Score: 130/165 (EXCELLENT)

Please respond:
[✅ Accept Appointment] [❌ Decline & Reschedule]

Thank you!
Metro Physical Therapy
─────────────────────────────────────────
```

### Step 5: WAITLIST & BACKFILL (UC5)
```
IF Patient Declines:
  1. Add patient to waitlist
  2. Look for high no-show risk patients who might want earlier slot
  3. Backfill the freed slot
  4. Try next best match for original patient

Example: If Maria declines Dr. Emily...
  → Offer Dr. James Wilson instead
  → Or offer Dr. Sarah's slot TOMORROW (continuity option)
```

### Step 6: AUDIT & RECONCILIATION (UC6)
```
📊 Complete Audit Log Generated:
─────────────────────────────────────
Session ID: SESSION_2025-11-20_093000
Provider: Dr. Sarah Johnson (T001)
Reason: Sick (flu)
Duration: November 20, 2025

Affected Appointments: 8
Successfully Reassigned: 7
HOD Manual Review: 1 (David Miller)
Waitlist: 0
Emails Sent: 8
Patient Responses: 
  • Accepted: 6
  • Declined: 1
  • Pending: 1

Revenue Impact: $960 preserved
Empty Slots Prevented: 8
Processing Time: 12 seconds
Compliance Verified: ✓ All assignments compliant
─────────────────────────────────────
```

---

## 🎯 Expected Outcomes by Patient

### ✅ Scenario A: PERFECT MATCHES (6 patients)
1. **Maria → Dr. Emily Ross** (130 pts EXCELLENT)
   - Gender match ✓, Specialty ✓, Location ✓
   - **Accepts immediately**

2. **Susan → Dr. Emily Ross** (125 pts EXCELLENT)
   - Female preference ✓, Orthopedic ✓
   - **Accepts immediately**

3. **John → Dr. Emily Ross** (105 pts EXCELLENT)
   - Flexible, good match
   - **Accepts immediately**

4. **Robert → Dr. Emily Ross** (110 pts EXCELLENT)
   - Orthopedic match ✓, Insurance OK ✓
   - **Accepts immediately**

5. **Lisa → Dr. James Wilson** (95 pts GOOD)
   - Sports Medicine OK, Female preference not met
   - **Accepts (no other option)**

6. **James Jr → Dr. James Wilson** (100 pts EXCELLENT)
   - New patient, Sports Medicine ✓, very flexible
   - **Accepts immediately**

### ⚠️ Scenario B: SPECIAL CASE (1 patient)
7. **Patricia → Dr. Michael Lee** (Continuity Match!)
   - Prefers male provider ✓
   - Has seen Dr. Michael before ✓
   - **BUT Dr. Michael unavailable today**
   - **Offered: Dr. Sarah TOMORROW** (continuity +30 pts)
   - **Decision: PENDING** (waiting for response)

### 🔴 Scenario C: HOD REVIEW (1 patient)
8. **David → HOD Review** (60 pts POOR)
   - High no-show risk (0.35)
   - Far location (12 miles, outside 10-mile max)
   - Low score
   - **Assigned to: Dr. Sarah Johnson (HOD) for manual review**
   - **Status: NEEDS_REVIEW** (orange in calendar)
   - **Action: Jessica calls David personally**

---

## 🎭 The Demo Script (5 Minutes)

### MINUTE 1: Setup the Crisis (30 sec)
```
"Good morning! It's 7:30 AM at Metro Physical Therapy.
Dr. Sarah Johnson just called in sick with severe flu.
She has 8 patients scheduled TODAY.

Let me show you how our AI system handles this crisis..."
```

### MINUTE 2: The Problem (30 sec)
```
[SHOW CALENDAR: http://localhost:8000/schedule.html]

"Here's Dr. Sarah's schedule - 8 appointments from 9 AM to 3:30 PM.
Look at these patients:
• Maria - post-surgical knee (needs urgent care)
• David - high no-show risk (might not even show up!)
• Patricia - prefers male providers (unique requirement)

Manually calling 8 patients would take 2+ hours.
Each needs a qualified replacement.
Let's see how AI solves this in seconds..."
```

### MINUTE 3: The AI Solution (2 min)
```
[CLICK: "Mark Unavailable" on Dr. Sarah]

"Watch this modal - I can mark her sick for 1 day or multiple days.
I'll choose 'Today only' for this demo."

[CLICK: "Mark Unavailable"]

"Now the magic happens...
[Point to loading popup]

The system is:
1. ✓ Marking Dr. Sarah unavailable
2. ✓ Finding all 8 affected appointments
3. ✓ Calculating priority scores (no-show risk, condition urgency)
4. ✓ Filtering qualified providers (certifications, availability)
5. ✓ Scoring 24 combinations (8 patients × 3 providers)
6. ✓ Making intelligent assignments
7. ✓ Sending personalized emails

[SUCCESS POPUP APPEARS]

Done! 8 appointments processed in 12 seconds.
7 automatically reassigned, 1 needs manual review."
```

### MINUTE 4: The Results (1 min)
```
[SHOW CALENDAR - Dr. Sarah now RED]

"Look at the results:
• Dr. Sarah - RED (unavailable)
• Dr. Emily Ross - 6 new patients (BLUE = pending confirmation)
• Dr. James Wilson - 2 new patients
• One patient (David) - ORANGE (HOD manual review needed)

[HOVER OVER MARIA'S APPOINTMENT]

See the AI reasoning:
⭐ Score: 130/165 pts (EXCELLENT match)
🏥 Specialty: +35 (Orthopedic specialist)
👥 Gender: +15 (Female provider, as preferred)
📍 Location: +15 (Same zip code)
... and more!

[CLICK: "View Details"]

Here's the complete audit log:
• All 8 patients processed
• Detailed scoring breakdown
• Compliance verified
• Complete transparency"
```

### MINUTE 5: The Patient Experience (30 sec)
```
[OPEN: http://localhost:8000/emails.html]

"Here are the 8 emails sent to patients.
[CLICK ON MARIA'S EMAIL]

Look at this:
• Clear explanation
• New provider details
• Match score explanation
• ONE-CLICK accept/decline buttons

Maria clicks 'Accept' → Appointment confirmed automatically!

If she declines → System offers next best match.

[SHOW HOD REVIEW CASE]

David Miller's case is flagged orange.
Why? High no-show risk + far location = low score.
Jessica will call him personally - AI knows when to hand off to humans!"
```

---

## 🎯 Key Demo Points to Emphasize

### 1. **Speed & Efficiency**
- Manual: 2+ hours of phone calls
- AI: 12 seconds, fully automated

### 2. **Intelligence & Personalization**
- 165-point scoring system
- 6 criteria: specialty, gender, location, experience, time, day
- Each patient gets BEST match, not just "any" provider

### 3. **Patient Satisfaction**
- Respects preferences (gender, location, day)
- Clear communication
- Easy accept/decline options
- Continuity of care prioritized

### 4. **Human-in-the-Loop**
- AI handles 87.5% (7/8 patients)
- Flags edge cases for human review
- Transparent reasoning (audit logs)
- Jessica stays in control

### 5. **Compliance & Safety**
- All certifications checked
- Insurance compatibility verified
- No appointments to unqualified providers
- Complete audit trail

### 6. **Real-World Complexity**
- Handles diverse patient needs
- Deals with unavailable backup providers
- Manages high-risk patients differently
- Supports date ranges (1 day to 2 weeks)

---

## ✅ Success Metrics to Share

```
Before AI:
❌ 2+ hours manual work
❌ Risk of errors/missed patients
❌ No transparency in decision-making
❌ Stressed receptionist
❌ Unhappy patients (long wait for callbacks)

After AI:
✅ 12 seconds processing time
✅ 100% patients contacted
✅ Complete audit trail
✅ Jessica handles only 1 edge case
✅ Patients get immediate notification
✅ $960 revenue preserved
✅ Zero empty slots
✅ All compliance requirements met
```

---

## 🎬 Closing Statement

```
"This isn't just automation - it's intelligent healthcare operations.

The AI doesn't replace Jessica - it empowers her.
She focuses on the 1 complex case (David),
while the AI handles the 7 routine reassignments perfectly.

Every decision is explainable. Every action is logged.
Patients are happier. Staff is less stressed.
Revenue is protected. Compliance is guaranteed.

This is the future of healthcare scheduling - 
and it's working TODAY at Metro Physical Therapy."
```

---

## 📋 Demo Checklist

**Before Demo:**
- [ ] Run `make restart` (resets all data)
- [ ] Open calendar: http://localhost:8000/schedule.html
- [ ] Open emails: http://localhost:8000/emails.html (in separate tab)
- [ ] Verify all 8 appointments visible under Dr. Sarah
- [ ] Verify Dr. Michael shows as unavailable (contrast)

**During Demo:**
- [ ] Tell the "7:30 AM phone call" story
- [ ] Show the 8 patients with their stories
- [ ] Click "Mark Unavailable" → Show modal
- [ ] Select "Today only" (default)
- [ ] Click "Mark Unavailable" → Show progress
- [ ] Point out the audit log
- [ ] Show Dr. Sarah turns RED
- [ ] Hover over reassigned appointments → Show scores
- [ ] Open emails page → Show sent emails
- [ ] Click Accept on one email → Show confirmation
- [ ] Highlight the HOD review case (David - orange)

**After Demo:**
- [ ] Show API documentation (http://localhost:8000/docs)
- [ ] Mention extensibility (more providers, more patients)
- [ ] Discuss real-world deployment scenarios

---

**Demo Duration:** 5 minutes  
**Audience:** Healthcare executives, IT decision-makers, Operations managers  
**Goal:** Show AI solving real operational problems with transparency and intelligence  
**Outcome:** "We need this system!"
