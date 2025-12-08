#!/usr/bin/env python3
"""
Test Event-Driven Backfill Implementation

This script tests the automatic backfill flow:
1. Provider unavailable → patients reassigned
2. Patient declines → added to waitlist + freed slot recorded
3. System automatically matches waitlist with freed slots
4. Waitlist patient gets the appointment
"""

import json
import time
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_waitlist():
    """Check current waitlist status"""
    waitlist_file = Path("data/waitlist.json")
    with open(waitlist_file, 'r') as f:
        waitlist = json.load(f)
    return waitlist

def check_freed_slots():
    """Check freed slots status"""
    slots_file = Path("data/freed_slots.json")
    with open(slots_file, 'r') as f:
        slots = json.load(f)
    return slots

def main():
    print_header("🧪 EVENT-DRIVEN BACKFILL TEST")
    
    print("\n📋 SCENARIO:")
    print("   1. Add a high no-show risk patient to waitlist")
    print("   2. Trigger provider unavailable workflow")
    print("   3. When patient declines, system should auto-backfill")
    print("   4. Waitlist patient gets the freed slot automatically")
    
    # Step 1: Setup - Add high no-show risk patient to waitlist
    print_header("Step 1: Setup Waitlist with High No-Show Risk Patient")
    
    waitlist_data = [
        {
            "waitlist_id": "WL_TEST001",
            "patient_id": "PAT_WAITLIST_001",
            "name": "Tom Anderson",
            "condition": "Shoulder pain",
            "no_show_risk": 0.85,  # HIGH no-show risk
            "priority": "MEDIUM",
            "requested_specialty": "Physical Therapy",
            "requested_location": "Downtown",
            "availability_windows": {
                "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "times": ["Morning", "Afternoon"]
            },
            "insurance": "Medicare",
            "current_appointment": None,
            "willing_to_move_up": True,
            "added_to_waitlist": "2025-11-21T08:00:00Z",
            "notes": "High no-show risk, willing to fill any available slot"
        }
    ]
    
    waitlist_file = Path("data/waitlist.json")
    with open(waitlist_file, 'w') as f:
        json.dump(waitlist_data, f, indent=2)
    
    print(f"✅ Added Tom Anderson to waitlist")
    print(f"   No-show risk: 85% (HIGH)")
    print(f"   Willing to move up: Yes")
    
    # Step 2: Check initial state
    print_header("Step 2: Initial State")
    
    waitlist = check_waitlist()
    freed_slots = check_freed_slots()
    
    print(f"📊 Waitlist: {len(waitlist)} patient(s)")
    for w in waitlist:
        print(f"   - {w['name']} (Risk: {w['no_show_risk']*100:.0f}%)")
    
    print(f"📊 Freed Slots: {len(freed_slots)} slot(s)")
    for s in freed_slots:
        print(f"   - {s.get('provider_id')} @ {s.get('time')} ({s.get('status')})")
    
    # Step 3: Trigger workflow
    print_header("Step 3: Trigger Provider Unavailable Workflow")
    print("💡 Trigger this manually:")
    print("   curl -X POST http://localhost:8000/api/trigger-workflow \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"trigger_type\":\"provider_unavailable\",\"provider_id\":\"T001\",\"reason\":\"sick\",\"start_date\":\"2025-11-21\",\"end_date\":\"2025-11-21\"}'")
    print("\n   Then decline one of the reassignment offers in the emails page")
    
    # Step 4: Instructions for testing
    print_header("Step 4: Testing Auto-Backfill")
    print("\n🔍 WHAT TO WATCH FOR:")
    print("   1. Open: http://localhost:8000/emails.html")
    print("   2. Click 'Decline' on any patient's reassignment offer")
    print("   3. System should automatically:")
    print("      ✅ Add patient to waitlist")
    print("      ✅ Record freed slot")
    print("      ✅ Match Tom Anderson (high no-show risk)")
    print("      ✅ Book Tom into the freed slot")
    print("      ✅ Send Tom a confirmation email")
    
    print_header("Step 5: Verify Auto-Backfill Worked")
    print("\n📊 Check these after declining an offer:")
    print("   1. Waitlist should show original patient + declined patient")
    print("   2. Freed slots should show one slot with status='backfilled'")
    print("   3. Tom Anderson should have a new appointment")
    print("   4. System logs should show: '🎉 Auto-backfilled with PAT_WAITLIST_001'")
    
    print_header("✅ Test Setup Complete!")
    print("\nℹ️  Run the workflow and test declining offers to see auto-backfill in action")
    print("   Logs: tail -f logs/api.log | grep -i backfill")

if __name__ == "__main__":
    main()

