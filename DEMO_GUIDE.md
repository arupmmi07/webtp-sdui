# Demo Guide - Patient Email Responses

> **📖 Full Use Case Documentation:** See [docs/USE_CASES_SIMPLIFIED.md](docs/USE_CASES_SIMPLIFIED.md) for complete workflow details.

## How It Works

When the system emails a patient about a provider change, the email includes **clickable links** that simulate patient responses:

### Email Content Example:
```
Hi Maria,

Dr. Sarah Johnson is unavailable. We'd like to reschedule you with 
Dr. Emily Ross on 2024-11-20 at 10:00 AM.

Please choose one of the following:

✅ CONFIRM: http://localhost:8000/api/patient-response?token=abc123&response=yes
❌ DECLINE: http://localhost:8000/api/patient-response?token=abc123&response=no
ℹ️  MORE INFO: http://localhost:8000/api/patient-response?token=abc123&response=info
```

---

## Demo Steps

### Step 1: Start the System
```bash
make dev
```

This starts:
- **API Server**: http://localhost:8000
- **Chat UI**: http://localhost:8501

### Step 2: Trigger a Workflow
In the Chat UI, type:
```
therapist departed T001
```

### Step 3: View the Email (Console Output)
Look at the console where you ran `make dev`. You'll see:
```
[EMAIL MOCK] ==================
[EMAIL MOCK] To: maria.r@email.com
[EMAIL MOCK] Subject: Appointment Rescheduling
[EMAIL MOCK] Body:
[EMAIL MOCK] ---
[EMAIL MOCK] Hi Maria, 
[EMAIL MOCK] ...
[EMAIL MOCK] ✅ CONFIRM: http://localhost:8000/api/patient-response?token=...&response=yes
[EMAIL MOCK] ==================
```

### Step 4: Simulate Patient Response

**Copy one of the links** from the console and open it in your browser:

#### Option A: Patient Confirms
```
http://localhost:8000/api/patient-response?token=abc123&response=yes
```
**Result:** Shows "Appointment Confirmed" page with details

#### Option B: Patient Declines
```
http://localhost:8000/api/patient-response?token=abc123&response=no
```
**Result:** Shows "Appointment Declined" page with next steps

#### Option C: Patient Wants More Info
```
http://localhost:8000/api/patient-response?token=abc123&response=info
```
**Result:** Shows provider details with option to confirm/decline

---

## Demo Scenarios for Different Patients

Since all patients use email in the demo, you can simulate different responses:

### Scenario 1: Happy Patient (Accepts Immediately)
```
1. Run workflow for T001
2. Copy the CONFIRM link
3. Open in browser
4. Shows: "Appointment Confirmed"
```

### Scenario 2: Hesitant Patient (Wants Info First)
```
1. Run workflow for T001
2. Copy the INFO link
3. Open in browser
4. Shows provider details
5. Click "YES, Confirm" on that page
```

### Scenario 3: Unhappy Patient (Declines)
```
1. Run workflow for T001
2. Copy the DECLINE link  
3. Open in browser
4. Shows: "Appointment Declined" with escalation info
```

---

## Testing Multiple Patients

The JSON data has 3 patients affected by T001's departure:

| Patient | Email | Appointment |
|---------|-------|-------------|
| PAT001 - Maria Rodriguez | maria.r@email.com | Nov 20, 10:00 AM |
| PAT002 - John Davis | john.d@email.com | Nov 21, 2:00 PM |
| PAT003 - Susan Lee | susan.l@email.com | Nov 22, 9:00 AM |

**To demo:**
1. Run workflow - it processes PAT001 first
2. Copy the link from console
3. Open in browser to simulate Maria's response
4. For demo purposes, explain that PAT002 and PAT003 would get similar emails

---

## What This Demonstrates

### For Stakeholders:
✅ **Patient Experience**: Clear, one-click confirmation  
✅ **Multi-Option**: Confirm, Decline, or Get Info  
✅ **Mobile-Friendly**: Works on phone, tablet, desktop  
✅ **Reduces Calls**: Patient responds directly, no phone tag

### For Technical Team:
✅ **Token-Based Security**: Each link has unique token  
✅ **Real-Time Workflow**: Patient response triggers next stage  
✅ **Audit Trail**: Every click is logged  
✅ **Scalable**: Same flow works for 1 or 1000 patients

---

## Real vs Demo

### Current (Demo):
- Email is printed to console
- Links work but don't trigger workflow
- Always processes successfully

### Production:
- Email actually sent via SendGrid/AWS SES
- Links trigger real workflow continuation
- Handles timeouts (no response after 24h)
- Sends reminders
- Escalates to phone call if needed

---

## Quick Demo Script

**For a 2-minute demo:**

1. **Start**: `make dev` 
2. **Trigger**: Type "therapist departed T001" in UI
3. **Show**: Console output with email links
4. **Click**: Copy CONFIRM link → Open in browser
5. **Result**: Show confirmation page
6. **Explain**: "In production, this happens automatically when patient clicks"

**For a 5-minute demo:**

1. Do above
2. **Show JSON data**: `cat data/patients.json` - 3 real patients
3. **Show workflow**: Explain 6 stages in UI
4. **Show alternatives**: Click INFO link → shows provider details
5. **Show decline**: Open DECLINE link → shows escalation path

---

## Troubleshooting

**Links don't work?**
- Make sure API is running on port 8000
- Check console for the actual token in the URL

**No email in console?**
- Look for `[EMAIL MOCK]` in the output
- Stage 4 (Consent) is where email is sent

**Want different patients?**
- Edit `data/patients.json`
- Add more appointments in `data/appointments.json`
- Restart with `make dev`


