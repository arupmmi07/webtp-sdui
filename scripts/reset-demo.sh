#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🔄 RESETTING DEMO TO INITIAL STATE                         ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Get today's date and tomorrow's date
TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -v+1d +%Y-%m-%d 2>/dev/null || date -d "+1 day" +%Y-%m-%d)
DAY_AFTER=$(date -v+2d +%Y-%m-%d 2>/dev/null || date -d "+2 days" +%Y-%m-%d)
DAY_OF_WEEK=$(date +%A)

echo "📅 Setting up demo for:"
echo "   Date: $TODAY ($DAY_OF_WEEK)"
echo ""

# Create backups directory if it doesn't exist
mkdir -p "$PROJECT_DIR/data/backups"

# Check if backups exist, if not create them from current state
if [ ! -f "$PROJECT_DIR/data/backups/appointments.json.template" ]; then
    echo "📦 Creating initial state templates..."
    cp "$PROJECT_DIR/data/appointments.json" "$PROJECT_DIR/data/backups/appointments.json.template"
    cp "$PROJECT_DIR/data/providers.json" "$PROJECT_DIR/data/backups/providers.json.template"
    cp "$PROJECT_DIR/data/patients.json" "$PROJECT_DIR/data/backups/patients.json.template"
    cp "$PROJECT_DIR/data/waitlist.json" "$PROJECT_DIR/data/backups/waitlist.json.template"
    cp "$PROJECT_DIR/data/freed_slots.json" "$PROJECT_DIR/data/backups/freed_slots.json.template"
    echo "✅ Templates created in data/backups/"
    echo ""
fi

# Restore from backups
echo "🔄 Restoring and updating data..."

# Update appointments to TODAY's date
source "$PROJECT_DIR/venv/bin/activate"
python - <<PYTHON_SCRIPT
import json
from datetime import datetime, timedelta

today = "$TODAY"

# Load template appointments
with open("$PROJECT_DIR/data/backups/appointments.json.template", "r") as f:
    appointments = json.load(f)

# Update all appointments to today with different times
# Create 8 appointments for demo (showing distribution)
appointment_times = [
    "09:00", "09:30", "10:00", "10:30", 
    "14:00", "14:30", "15:00", "15:30"
]

for i in range(min(8, len(appointments))):
    time = appointment_times[i]
    appointments[i]["date"] = f"{today}T{time}:00"
    appointments[i]["time"] = time
    appointments[i]["provider_id"] = "T001"  # All initially with Sarah
    appointments[i]["status"] = "scheduled"
    appointments[i]["reassigned"] = False
    appointments[i]["confirmation_status"] = "confirmed"

# Add special LOW-MATCH appointment for David Rodriguez (PAT_LOWMATCH)
# This patient will have very low match scores and go to waitlist
appointments.append({
    "appointment_id": "A_LOWMATCH",
    "patient_id": "PAT_LOWMATCH",
    "provider_id": "T001",
    "date": f"{today}T16:00:00",
    "time": "16:00",
    "duration_minutes": 60,
    "appointment_type": "Initial Evaluation",
    "status": "scheduled",
    "reassigned": False,
    "confirmation_status": "confirmed",
    "notes": "Complex post-surgical case - likely low match score → waitlist demo",
    "created_at": f"{today}T10:00:00Z",
    "original_provider_id": "T001"
})

# Save updated appointments
with open("$PROJECT_DIR/data/appointments.json", "w") as f:
    json.dump(appointments, f, indent=2)

print("✅ 9 appointments created for today (Dr. Sarah Johnson)")
print("   → 8 regular appointments (good matches)")
print("   → 1 low-match appointment (David Rodriguez - will go to waitlist)")
PYTHON_SCRIPT

# Update providers - reset and add available slots for continuity
python - <<PYTHON_SCRIPT
import json
from datetime import datetime, timedelta

today_str = "$TODAY"
today = datetime.strptime(today_str, "%Y-%m-%d")
tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
day_after = (today + timedelta(days=2)).strftime("%Y-%m-%d")

# Load template providers
with open("$PROJECT_DIR/data/backups/providers.json.template", "r") as f:
    providers = json.load(f)

# Reset all providers - ALL AVAILABLE for demo
for provider in providers:
    provider["status"] = "active"
    provider["unavailable_dates"] = []  # NO ONE unavailable by default
    provider["current_patient_load"] = 0  # WIP - not used in scoring
    
    # Add available_slots for CONTINUITY feature (UC3: +30pts)
    # Sarah (T001) has slots tomorrow and day after for continuity option
    if provider["provider_id"] == "T001":
        provider["available_slots"] = [
            {"date": tomorrow, "time": "09:00", "available": True},
            {"date": tomorrow, "time": "10:00", "available": True},
            {"date": tomorrow, "time": "14:00", "available": True},
            {"date": day_after, "time": "09:00", "available": True},
            {"date": day_after, "time": "10:00", "available": True}
        ]
    else:
        # Other providers have today's slots available
        provider["available_slots"] = [
            {"date": today_str, "time": "09:00", "available": True},
            {"date": today_str, "time": "10:00", "available": True},
            {"date": today_str, "time": "14:00", "available": True},
            {"date": today_str, "time": "15:00", "available": True}
        ]

# Save updated providers
with open("$PROJECT_DIR/data/providers.json", "w") as f:
    json.dump(providers, f, indent=2)

print(f"✅ All providers available with slots (Sarah has continuity slots for {tomorrow})")
PYTHON_SCRIPT

# Restore other files directly
cp "$PROJECT_DIR/data/backups/patients.json.template" "$PROJECT_DIR/data/patients.json"
cp "$PROJECT_DIR/data/backups/waitlist.json.template" "$PROJECT_DIR/data/waitlist.json"
cp "$PROJECT_DIR/data/backups/freed_slots.json.template" "$PROJECT_DIR/data/freed_slots.json"

echo "✅ Patients restored"
echo "✅ Waitlist cleared"
echo "✅ Freed slots cleared"

# Clear sent emails
echo "[]" > "$PROJECT_DIR/data/emails.json"
echo "✅ Sent emails cleared"
echo ""

# Clear email preview session if exists
if [ -f "$PROJECT_DIR/demo/.streamlit_session" ]; then
    rm "$PROJECT_DIR/demo/.streamlit_session"
    echo "✅ Email session cleared"
fi

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   ✅ DEMO RESET COMPLETE!                                    ║"
echo "║                                                               ║"
echo "║   📅 Demo Date: $TODAY ($DAY_OF_WEEK)"
echo "║                                                               ║"
echo "║   🏥 INITIAL STATE:                                          ║"
echo "║   ✅ Dr. Sarah Johnson (Orthopedic PT) - AVAILABLE           ║"
echo "║      • Has 3 appointments at 9:00, 9:30, 10:00               ║"
echo "║   ✅ Dr. Emily Ross (Orthopedic PT) - AVAILABLE ⭐           ║"
echo "║   ✅ Dr. James Wilson (Acupuncture PT) - AVAILABLE           ║"
echo "║   ✅ Dr. Michael Lee (Geriatric PT) - AVAILABLE              ║"
echo "║                                                               ║"
echo "║   💡 Demo-friendly: Emily has same specialty as Sarah!       ║"
echo "║      Perfect for showing specialty-based matching logic!     ║"
echo "║                                                               ║"
echo "║   📋 TEST SCENARIO:                                          ║"
echo "║   1. View Calendar: http://localhost:8000/schedule.html      ║"
echo "║      → ALL 4 doctors showing as AVAILABLE ✅                 ║"
echo "║      → Sarah has 3 appointments at 9:00, 9:30, 10:00         ║"
echo "║                                                               ║"
echo "║   2. Click '🚫 Mark Unavailable' for Dr. Sarah Johnson       ║"
echo "║      → System marks Sarah unavailable                        ║"
echo "║      → AI workflow triggered automatically 🤖                ║"
echo "║      → PERFECT MATCH: Emily has same specialty! ⭐           ║"
echo "║      → Reassigns orthopedic patients to Emily (same spec)    ║"
echo "║      → James & Michael available as backups                  ║"
echo "║      → Sends emails to patients with Accept/Decline links    ║"
echo "║                                                               ║"
echo "║   3. Check Calendar & Emails                                 ║"
echo "║      → Sarah now RED (unavailable)                           ║"
echo "║      → Orthopedic appointments reassigned to Emily! ⭐       ║"
echo "║      → View emails: http://localhost:8000/emails.html        ║"
echo "║      → Smart specialty-based matching demonstrated ✨        ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

