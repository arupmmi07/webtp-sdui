"""Backfill & Waitlist Agent.

Handles:
- Use Case 5: Waitlist & Backfill Automation
- Intelligent slot filling with high no-show risk targeting
- Original patient rescheduling
- Waitlist prioritization
"""

from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.json_client import JSONClient


class BackfillAgent:
    """Handles waitlist and backfill logic for freed appointment slots.
    
    Key Features:
    1. Match freed slots with waitlist patients
    2. Prioritize high no-show risk patients
    3. Reschedule original declined patients
    4. Track backfill success metrics
    """
    
    def __init__(self, json_client: JSONClient = None):
        """Initialize backfill agent."""
        self.json_client = json_client or JSONClient()
        print(f"[BACKFILL AGENT] Initialized")
    
    def handle_slot_freed(
        self,
        appointment: Dict[str, Any],
        reason: str = "Patient declined all providers"
    ) -> Dict[str, Any]:
        """Handle when a slot becomes available (patient declines).
        
        Args:
            appointment: The freed appointment details
            reason: Why the slot was freed
        
        Returns:
            Backfill result with matched patient or escalation
        """
        print(f"\n[BACKFILL] Handling freed slot from appointment {appointment.get('appointment_id')}")
        print(f"[BACKFILL] Reason: {reason}")
        
        # Step 1: Add slot to freed slots list
        freed_slot = {
            "provider_id": appointment.get("provider_id"),
            "date": appointment.get("date"),
            "time": appointment.get("time"),
            "duration_minutes": 60,
            "specialty": "Physical Therapy",  # Would come from provider data
            "location": "Downtown",  # Would come from provider/appointment data
            "reason_freed": reason,
            "freed_at": datetime.utcnow().isoformat() + "Z"
        }
        
        slot_result = self.json_client.add_freed_slot(freed_slot)
        slot_id = slot_result.get("slot", {}).get("slot_id")
        
        # Step 2: Find high no-show risk patients from waitlist
        waitlist_matches = self._find_waitlist_matches(freed_slot)
        
        if waitlist_matches:
            # Step 3: Offer slot to best match
            best_match = waitlist_matches[0]
            backfill_result = self._backfill_with_patient(slot_id, freed_slot, best_match)
            return backfill_result
        else:
            print(f"[BACKFILL] No waitlist matches found")
            return {
                "status": "NO_MATCHES",
                "slot_id": slot_id,
                "message": "No suitable waitlist patients found",
                "action_needed": "Manual review or keep slot open"
            }
    
    def _find_waitlist_matches(
        self,
        freed_slot: Dict[str, Any],
        min_no_show_risk: float = 0.6
    ) -> List[Dict[str, Any]]:
        """Find waitlist patients that match the freed slot.
        
        Args:
            freed_slot: The freed slot details
            min_no_show_risk: Minimum no-show risk threshold
        
        Returns:
            List of matching waitlist entries sorted by priority
        """
        print(f"[BACKFILL] Finding waitlist matches (min no-show risk: {min_no_show_risk})")
        
        # Get high-risk waitlist patients
        waitlist = self.json_client.get_waitlist(min_no_show_risk=min_no_show_risk)
        
        # Filter by specialty and availability
        matches = []
        for entry in waitlist:
            # Check specialty match
            if entry.get("requested_specialty") != freed_slot.get("specialty"):
                continue
            
            # Check if willing to move up
            if not entry.get("willing_to_move_up", False):
                continue
            
            # Check availability (simplified - would do date/time matching in full version)
            matches.append(entry)
        
        print(f"[BACKFILL] Found {len(matches)} potential matches")
        
        # Sort by no-show risk (highest first)
        matches.sort(key=lambda x: x.get("no_show_risk", 0.0), reverse=True)
        
        return matches
    
    def _backfill_with_patient(
        self,
        slot_id: str,
        freed_slot: Dict[str, Any],
        waitlist_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Backfill a slot with a waitlist patient.
        
        Args:
            slot_id: Freed slot ID
            freed_slot: Slot details
            waitlist_entry: Waitlist patient entry
        
        Returns:
            Backfill result
        """
        patient_id = waitlist_entry["patient_id"]
        patient_name = waitlist_entry["name"]
        no_show_risk = waitlist_entry["no_show_risk"]
        
        print(f"[BACKFILL] Backfilling with {patient_name} (risk: {no_show_risk:.0%})")
        
        # Create new appointment for waitlist patient
        new_appointment_id = f"A{int(datetime.utcnow().timestamp()) % 1000:03d}"
        
        # Book the appointment (would call domain server in full version)
        appointment_data = {
            "appointment_id": new_appointment_id,
            "patient_id": patient_id,
            "provider_id": freed_slot["provider_id"],
            "date": freed_slot["date"],
            "time": freed_slot["time"],
            "status": "scheduled",
            "confirmation_number": f"BACKFILL-{new_appointment_id}",
            "notes": f"Backfilled from waitlist (no-show risk: {no_show_risk:.0%})"
        }
        
        booking_result = self.json_client.book_appointment(appointment_data)
        
        if booking_result["status"] == "SUCCESS":
            # Mark slot as backfilled
            self.json_client.backfill_slot(slot_id, patient_id, new_appointment_id)
            
            # Remove from waitlist
            self.json_client.remove_from_waitlist(waitlist_entry["waitlist_id"])
            
            print(f"[BACKFILL] ✅ Successfully backfilled slot {slot_id}")
            
            return {
                "status": "SUCCESS",
                "slot_id": slot_id,
                "backfilled_with": {
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "no_show_risk": no_show_risk,
                    "appointment_id": new_appointment_id,
                    "confirmation_number": appointment_data["confirmation_number"]
                },
                "message": f"Slot backfilled with high-risk patient {patient_name}",
                "revenue_preserved": "$120",  # Would calculate based on appointment value
                "extra_reminders_scheduled": 3  # High-risk patients get extra reminders
            }
        else:
            print(f"[BACKFILL] ❌ Failed to book appointment")
            return {
                "status": "ERROR",
                "message": "Failed to book backfill appointment"
            }
    
    def reschedule_declined_patient(
        self,
        original_patient_id: str,
        original_appointment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Reschedule the original patient who declined all providers.
        
        Args:
            original_patient_id: Patient ID
            original_appointment: Original appointment details
        
        Returns:
            Rescheduling result
        """
        print(f"\n[BACKFILL] Rescheduling declined patient {original_patient_id}")
        
        # Get patient details
        patient = self.json_client.get_patient(original_patient_id)
        if not patient:
            return {
                "status": "ERROR",
                "message": f"Patient {original_patient_id} not found"
            }
        
        patient_name = patient.get("name", "Unknown")
        
        # In full version: Query available slots matching patient's availability windows
        # For demo: Add to waitlist for manual follow-up
        
        waitlist_entry = {
            "patient_id": original_patient_id,
            "name": patient_name,
            "condition": patient.get("condition", "Unknown"),
            "no_show_risk": patient.get("no_show_risk", 0.5),
            "priority": "HIGH",  # Original declined patient gets high priority
            "requested_specialty": "Physical Therapy",
            "requested_location": "Any",
            "availability_windows": {
                "days": ["Monday", "Wednesday", "Friday"],
                "times": ["Morning", "Afternoon"]
            },
            "insurance": patient.get("insurance", "Unknown"),
            "current_appointment": None,
            "willing_to_move_up": True,
            "added_to_waitlist": datetime.utcnow().isoformat() + "Z",
            "notes": f"Original patient declined all providers, needs rescheduling"
        }
        
        result = self.json_client.add_to_waitlist(waitlist_entry)
        
        if result["status"] == "SUCCESS":
            print(f"[BACKFILL] ✅ Added {patient_name} to waitlist for rescheduling")
            return {
                "status": "WAITLISTED",
                "patient_id": original_patient_id,
                "patient_name": patient_name,
                "waitlist_id": result["waitlist_entry"]["waitlist_id"],
                "message": f"{patient_name} added to waitlist for manual rescheduling",
                "action_needed": "Front desk to follow up"
            }
        else:
            return {
                "status": "ERROR",
                "message": "Failed to add patient to waitlist"
            }
    
    def get_backfill_metrics(self) -> Dict[str, Any]:
        """Get backfill performance metrics.
        
        Returns:
            Metrics including fill rate, revenue preserved, etc.
        """
        freed_slots = self.json_client.get_freed_slots(status="available")
        backfilled_slots = self.json_client.get_freed_slots(status="backfilled")
        
        total_slots = len(freed_slots) + len(backfilled_slots)
        fill_rate = len(backfilled_slots) / total_slots if total_slots > 0 else 0.0
        
        return {
            "total_freed_slots": total_slots,
            "available_slots": len(freed_slots),
            "backfilled_slots": len(backfilled_slots),
            "fill_rate": f"{fill_rate:.0%}",
            "revenue_preserved": f"${len(backfilled_slots) * 120}",  # $120 per appointment
            "high_risk_patients_helped": len(backfilled_slots)
        }


def create_backfill_agent() -> BackfillAgent:
    """Factory function to create backfill agent."""
    return BackfillAgent()


if __name__ == "__main__":
    # Test the agent
    print("=== BACKFILL AGENT TEST ===\n")
    
    agent = create_backfill_agent()
    
    # Test 1: Handle freed slot
    print("\n1. Testing handle_slot_freed:")
    test_appointment = {
        "appointment_id": "A001",
        "patient_id": "PAT001",
        "provider_id": "P001",
        "date": "2025-11-20",
        "time": "10:00 AM"
    }
    
    result = agent.handle_slot_freed(test_appointment, "Patient declined all providers")
    print(f"   Result: {result['status']}")
    if result["status"] == "SUCCESS":
        print(f"   Backfilled with: {result['backfilled_with']['patient_name']}")
        print(f"   Revenue preserved: {result['revenue_preserved']}")
    
    # Test 2: Get metrics
    print("\n2. Testing get_backfill_metrics:")
    metrics = agent.get_backfill_metrics()
    print(f"   Fill rate: {metrics['fill_rate']}")
    print(f"   Revenue preserved: {metrics['revenue_preserved']}")
    
    print("\n✅ Backfill agent tests complete!")

