# Test Scenario: Provider Unavailability & Patient Reassignment

This document describes the complete test scenario for demonstrating the provider unavailability workflow and patient reassignment logic.

## 🎯 Scenario Overview

**Situation:** Dr. Sarah Johnson (T001) calls in sick. She has 3 patients scheduled for today. The system needs to automatically reassign these patients to other available providers based on:
- Patient preferences (gender, specialty, location)
- Provider availability and capacity
- Appointment priority
- Distance/location constraints

## 📋 Initial State

### Provider: Dr. Sarah Johnson (T001)
- **Status:** Initially active, will be marked as "sick"
- **Unavailable Dates:** Nov 19-21, 2025
- **Scheduled Patients:** 3 patients (PAT001, PAT002, PAT003)
- **Location:** Metro PT Downtown

### Patients Affected:
1. **Maria Rodriguez (PAT001)** - Post-surgical knee, prefers female providers
2. **John Davis (PAT002)** - Lower back pain, no gender preference
3. **Susan Lee (PAT003)** - Hip replacement recovery, prefers female providers

### Available Providers:
- **Dr. Emily Ross (P001)** - Female, Orthopedic, Main Clinic, 60% capacity
- **Dr. James Wilson (P003)** - Male, Sports Medicine, Westside, 45% capacity
- **Dr. Michael Lee (P004)** - Male, Orthopedic, Main Clinic, 88% capacity (nearly full)

## 🚀 Test Steps

### Step 1: Reset to Initial State
```bash
make reset-demo
```

This restores all data to the original state:
- T001 marked as active
- All 3 patients scheduled with T001
- Waitlist cleared
- Email history cleared

### Step 2: View Initial Schedule
```bash
# Open calendar
open http://localhost:8000/schedule.html

# Navigate to: Wednesday, November 19, 2025
# You should see:
# - Dr. Sarah Johnson column with 3 appointments
# - Other providers with their schedules
```

### Step 3: Trigger the Workflow
```bash
# Open chat UI
open http://localhost:8501/

# Type this command:
provider T001 sick
```

### Step 4: Observe the Workflow

The system will execute these stages:

**Stage 1: Trigger Detection**
- Identifies T001 is unavailable
- Finds 3 affected appointments
- Calculates priority scores

**Stage 2: Filter Candidates**
- Finds available providers
- Filters by specialty (orthopedic)
- Filters by location proximity
- Filters by gender preference (where applicable)

**Stage 3: Score & Rank**
- Scores providers based on:
  - Specialty match
  - Gender preference match
  - Location proximity
  - Current capacity
  - Patient history

**Stage 4: Patient Engagement**
- Sends email offers to patients
- Includes confirmation links
- Shows new provider details

**Stage 5: Booking**
- Books appointments with new providers
- Updates provider capacity
- Creates confirmation numbers

**Stage 6: Audit**
- Logs all changes
- Tracks reassignments
- Records reasons

### Step 5: View Results

**Check Calendar:**
```bash
open http://localhost:8000/schedule.html
# Navigate to Nov 19, 2025
# You should see:
# - Dr. Sarah Johnson column: ALL RED (unavailable)
# - Patients moved to other provider columns
# - Before/After comparison in chat UI
```

**Check Emails:**
```bash
open http://localhost:8000/emails.html
# You should see:
# - 3 emails sent to patients
# - Offer details with new provider info
# - Confirmation links
```

**Check Chat UI:**
```bash
# Scroll through chat to see:
# - Stage-by-stage execution
# - Before/After appointment comparison
# - Assignment summary
```

## 📊 Expected Results

### Patient Reassignments (Based on USE_CASES.md Logic):

1. **Maria Rodriguez (PAT001)**
   - **Preference:** Female provider, orthopedic
   - **Expected Assignment:** Dr. Emily Ross (P001)
   - **Reason:** Female, orthopedic, available, good capacity

2. **John Davis (PAT002)**
   - **Preference:** No gender preference, orthopedic
   - **Expected Assignment:** Dr. Emily Ross (P001) or Dr. Michael Lee (P004)
   - **Reason:** Both orthopedic, good availability

3. **Susan Lee (PAT003)**
   - **Preference:** Female provider, orthopedic  
   - **Expected Assignment:** Dr. Emily Ross (P001)
   - **Reason:** Female, orthopedic, matches preference

### Calendar Visual:
```
Before (Nov 19, 2025):
┌──────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Time │ Dr. Sarah   │ Dr. Emily   │ Dr. James   │ Dr. Michael │
│      │ (T001)      │ (P001)      │ (P003)      │ (P004)      │
├──────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ 9:00 │ Maria R.    │ —           │ —           │ —           │
│ 9:30 │ John D.     │ —           │ —           │ —           │
│10:00 │ Susan L.    │ —           │ —           │ —           │
└──────┴─────────────┴─────────────┴─────────────┴─────────────┘

After (Nov 19, 2025):
┌──────┬─────────────┬─────────────┬─────────────┬─────────────┐
│ Time │ Dr. Sarah   │ Dr. Emily   │ Dr. James   │ Dr. Michael │
│      │ (T001)      │ (P001)      │ (P003)      │ (P004)      │
├──────┼─────────────┼─────────────┼─────────────┼─────────────┤
│ 9:00 │🔴 UNAVAIL   │ Maria R. ✨ │ —           │ —           │
│ 9:30 │🔴 UNAVAIL   │ John D. ✨  │ —           │ —           │
│10:00 │🔴 UNAVAIL   │ Susan L. ✨ │ —           │ —           │
└──────┴─────────────┴─────────────┴─────────────┴─────────────┘
```

## 🔄 Reset and Test Again

To run the scenario multiple times:

```bash
# Reset data
make reset-demo

# Restart services (if needed)
make restart

# Run test again
# Go to http://localhost:8501/
# Type: provider T001 sick
```

## 🧪 Variations to Test

### Variation 1: Different Provider
```bash
make reset-demo
# Then in chat: provider P001 on_leave
```

### Variation 2: Specific Date
```bash
make reset-demo
# Then in chat: provider T001 unavailable 2025-11-20
```

### Variation 3: Multiple Providers
```bash
make reset-demo
# Edit data/providers.json to mark multiple providers as unavailable
# Then in chat: provider T001 sick
```

## 📝 Test Checklist

- [ ] Initial state shows T001 with 3 appointments
- [ ] Calendar displays all providers correctly
- [ ] Running "provider T001 sick" triggers workflow
- [ ] Chat shows all 6 stages executing
- [ ] Patients are reassigned based on preferences
- [ ] Calendar shows T001 column in red
- [ ] Appointments moved to new provider columns
- [ ] 3 emails sent to patients
- [ ] Before/After comparison displayed
- [ ] Reset command works
- [ ] Can run test multiple times

## 🎓 Demo Script (5 Minutes)

**Opening:**
> "Let me show you how our AI Assistant handles provider unavailability automatically."

**Step 1:** Show Initial Calendar
> "Here's Wednesday, Nov 19th. Dr. Sarah Johnson has 3 patients scheduled."

**Step 2:** Trigger Event
> "She just called in sick. I'll tell the system: 'provider T001 sick'"

**Step 3:** Watch Magic Happen
> "Watch as the system automatically:
> - Identifies affected patients
> - Finds replacement providers
> - Matches based on preferences
> - Sends email notifications
> - Updates the schedule"

**Step 4:** Show Results
> "Look at the calendar now - Dr. Sarah's column is red, and all patients 
> are reassigned to Dr. Emily Ross, who matches their preferences."

**Step 5:** Show Emails
> "And each patient received a professional email with their new appointment details."

**Closing:**
> "This entire process took 10 seconds instead of 30 minutes of manual phone calls. 
> The receptionist can reset and test this anytime with one command."

## 🐛 Troubleshooting

**Issue:** Reset doesn't work
```bash
# Manually restore backups
cp data/backups/*.json data/
make restart
```

**Issue:** No appointments showing
```bash
# Check data files exist
ls -la data/*.json
# Restart API
make restart
```

**Issue:** Wrong date showing
```bash
# Update appointments.json dates to current or test date
# Or navigate to Nov 19, 2025 in calendar
```

## 📚 Related Documents

- `USE_CASES.md` - Detailed use case descriptions
- `DEMO_STORY.md` - Demo scenarios and narratives
- `docs/PATIENT_LOCATION_RESEARCH.md` - Location matching logic
- `README.md` - Project overview and setup

