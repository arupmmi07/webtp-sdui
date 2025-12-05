"""JSON File Client - Dead simple data source.

This reads/writes from JSON files in the data/ folder.
NO setup needed - just works!

Files:
- data/appointments.json
- data/providers.json
- data/patients.json
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class JSONClient:
    """Simple JSON file client for reading appointment/provider/patient data."""
    
    def __init__(self, data_dir: str = None):
        """Initialize JSON client.
        
        Args:
            data_dir: Directory containing JSON files (default: data/)
        """
        if data_dir is None:
            # Default to data/ folder in project root
            project_root = Path(__file__).parent.parent
            data_dir = project_root / "data"
        
        self.data_dir = Path(data_dir)
        self.appointments_file = self.data_dir / "appointments.json"
        self.providers_file = self.data_dir / "providers.json"
        self.patients_file = self.data_dir / "patients.json"
        self.waitlist_file = self.data_dir / "waitlist.json"
        self.freed_slots_file = self.data_dir / "freed_slots.json"
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ JSON Client initialized (data dir: {self.data_dir})")
    
    def _load_json(self, file_path: Path) -> List[Dict[str, Any]]:
        """Load JSON file."""
        if not file_path.exists():
            print(f"⚠️  File not found: {file_path}")
            return []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON in {file_path}: {str(e)}")
            return []
        except Exception as e:
            print(f"❌ Error reading {file_path}: {str(e)}")
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict[str, Any]]) -> bool:
        """Save JSON file."""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving {file_path}: {str(e)}")
            return False
    
    # ===== APPOINTMENTS =====
    
    def get_appointments_for_provider(self, provider_id: str, status: str = "scheduled") -> List[Dict[str, Any]]:
        """Get all appointments for a provider.
        
        Args:
            provider_id: Provider ID (e.g., "T001")
            status: Filter by status (scheduled, completed, cancelled)
        
        Returns:
            List of appointment dictionaries
        """
        appointments = self._load_json(self.appointments_file)
        
        # Filter by provider_id and status
        filtered = [
            apt for apt in appointments 
            if apt.get("provider_id") == provider_id 
            and apt.get("status", "").lower() == status.lower()
        ]
        
        print(f"📋 Found {len(filtered)} {status} appointments for {provider_id}")
        return filtered
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict[str, Any]]:
        """Get single appointment by ID.
        
        Args:
            appointment_id: Appointment ID (e.g., "A001")
        
        Returns:
            Appointment dictionary or None
        """
        appointments = self._load_json(self.appointments_file)
        
        for apt in appointments:
            if apt.get("appointment_id") == appointment_id:
                return apt
        
        print(f"⚠️  Appointment {appointment_id} not found")
        return None
    
    def book_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Book/update an appointment.
        
        Args:
            appointment_data: Appointment details
        
        Returns:
            Success response with confirmation
        """
        appointments = self._load_json(self.appointments_file)
        
        # Check if appointment already exists (update) or new (append)
        appointment_id = appointment_data.get("appointment_id")
        found = False
        
        for i, apt in enumerate(appointments):
            if apt.get("appointment_id") == appointment_id:
                # Update existing
                appointments[i] = appointment_data
                found = True
                break
        
        if not found:
            # Add new appointment
            appointments.append(appointment_data)
        
        # Save to file
        if self._save_json(self.appointments_file, appointments):
            print(f"✅ Appointment {'updated' if found else 'created'}: {appointment_id}")
            return {
                "status": "SUCCESS",
                "appointment_id": appointment_id,
                "confirmation_number": appointment_data.get("confirmation_number", "CONF-AUTO"),
                "message": f"Appointment {'updated' if found else 'created'} in JSON file"
            }
        else:
            return {
                "status": "ERROR",
                "message": "Failed to save appointment"
            }
    
    # ===== PROVIDERS =====
    
    def get_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get provider by ID.
        
        Args:
            provider_id: Provider ID (e.g., "P001")
        
        Returns:
            Provider dictionary or None
        """
        providers = self._load_json(self.providers_file)
        
        for provider in providers:
            if provider.get("provider_id") == provider_id:
                return provider
        
        print(f"⚠️  Provider {provider_id} not found")
        return None
    
    def get_all_providers(self, status: str = "active") -> List[Dict[str, Any]]:
        """Get all providers.
        
        Args:
            status: Filter by status (active, inactive, sick, on_leave)
        
        Returns:
            List of provider dictionaries
        """
        providers = self._load_json(self.providers_file)
        
        if status:
            filtered = [p for p in providers if p.get("status", "").lower() == status.lower()]
        else:
            filtered = providers
        
        print(f"👥 Found {len(filtered)} {status} providers")
        return filtered
    
    # ===== PATIENTS =====
    
    def update_appointment(self, appointment_id: str, updates: dict) -> bool:
        """Update an appointment with new data."""
        try:
            appointments = self._load_json(self.appointments_file)
            for apt in appointments:
                if apt.get('appointment_id') == appointment_id:
                    apt.update(updates)
                    self._save_json(self.appointments_file, appointments)
                    print(f"✅ Updated appointment {appointment_id}: {updates}")
                    return True
            print(f"❌ Appointment {appointment_id} not found")
            return False
        except Exception as e:
            print(f"❌ Error updating appointment: {e}")
            return False
    
    def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment by setting status to 'cancelled'."""
        return self.update_appointment(appointment_id, {"status": "cancelled"})
    
    def reassign_appointment(self, appointment_id: str, new_provider_id: str, reason: str = "Provider unavailable") -> bool:
        """Reassign an appointment to a new provider."""
        return self.update_appointment(appointment_id, {
            "provider_id": new_provider_id,
            "status": "rescheduled",
            "reassignment_reason": reason
        })
    
    def get_all_appointments(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all appointments.
        
        Args:
            status: Optional filter by status (scheduled, completed, cancelled, rescheduled)
        
        Returns:
            List of appointment dictionaries
        """
        appointments = self._load_json(self.appointments_file)
        
        if status:
            filtered = [a for a in appointments if a.get("status", "").lower() == status.lower()]
        else:
            filtered = appointments
        
        print(f"📋 Found {len(filtered)} appointments" + (f" with status '{status}'" if status else ""))
        return filtered
    
    # ===== PATIENTS =====
    
    def get_patient(self, patient_id: str) -> Optional[Dict[str, Any]]:
        """Get patient by ID.
        
        Args:
            patient_id: Patient ID (e.g., "PAT001")
        
        Returns:
            Patient dictionary or None
        """
        patients = self._load_json(self.patients_file)
        
        for patient in patients:
            if patient.get("patient_id") == patient_id:
                return patient
        
        print(f"⚠️  Patient {patient_id} not found")
        return None
    
    def get_all_patients(self) -> List[Dict[str, Any]]:
        """Get all patients.
        
        Returns:
            List of patient dictionaries
        """
        patients = self._load_json(self.patients_file)
        print(f"👥 Found {len(patients)} patients")
        return patients
    
    # ===== WAITLIST =====
    
    def get_waitlist(self, priority: Optional[str] = None, min_no_show_risk: Optional[float] = None) -> List[Dict[str, Any]]:
        """Get waitlist entries.
        
        Args:
            priority: Filter by priority (HIGH, MEDIUM, LOW)
            min_no_show_risk: Minimum no-show risk threshold (0.0-1.0)
        
        Returns:
            List of waitlist entries sorted by priority and no-show risk
        """
        waitlist = self._load_json(self.waitlist_file)
        
        # Apply filters
        filtered = waitlist
        if priority:
            filtered = [w for w in filtered if w.get("priority", "").upper() == priority.upper()]
        if min_no_show_risk is not None:
            filtered = [w for w in filtered if w.get("no_show_risk", 0.0) >= min_no_show_risk]
        
        # Sort by no-show risk (descending)
        filtered.sort(key=lambda x: x.get("no_show_risk", 0.0), reverse=True)
        
        print(f"📋 Found {len(filtered)} waitlist entries")
        return filtered
    
    def add_to_waitlist(self, waitlist_entry: Dict[str, Any]) -> Dict[str, Any]:
        """Add patient to waitlist.
        
        Args:
            waitlist_entry: Waitlist entry data
        
        Returns:
            Created waitlist entry with ID
        """
        waitlist = self._load_json(self.waitlist_file)
        
        # Generate ID if not provided
        if "waitlist_id" not in waitlist_entry:
            # Only consider numeric IDs (WL001, WL002, etc.), ignore test IDs like WL_TEST001
            numeric_ids = []
            for w in waitlist:
                if "waitlist_id" in w:
                    try:
                        # Extract numeric part after "WL"
                        id_num = int(w["waitlist_id"].replace("WL", ""))
                        numeric_ids.append(id_num)
                    except ValueError:
                        # Skip non-numeric IDs (like WL_TEST001)
                        continue
            
            max_id = max(numeric_ids, default=0)
            waitlist_entry["waitlist_id"] = f"WL{max_id + 1:03d}"
        
        waitlist.append(waitlist_entry)
        
        if self._save_json(self.waitlist_file, waitlist):
            print(f"✅ Added to waitlist: {waitlist_entry['waitlist_id']}")
            return {"status": "SUCCESS", "waitlist_entry": waitlist_entry}
        else:
            return {"status": "ERROR", "message": "Failed to save waitlist"}
    
    def remove_from_waitlist(self, waitlist_id: str) -> bool:
        """Remove patient from waitlist.
        
        Args:
            waitlist_id: Waitlist entry ID
        
        Returns:
            Success status
        """
        waitlist = self._load_json(self.waitlist_file)
        original_count = len(waitlist)
        
        waitlist = [w for w in waitlist if w.get("waitlist_id") != waitlist_id]
        
        if len(waitlist) < original_count:
            if self._save_json(self.waitlist_file, waitlist):
                print(f"✅ Removed from waitlist: {waitlist_id}")
                return True
        
        print(f"⚠️  Waitlist entry {waitlist_id} not found")
        return False
    
    # ===== FREED SLOTS =====
    
    def get_freed_slots(self, status: str = "available") -> List[Dict[str, Any]]:
        """Get freed appointment slots.
        
        Args:
            status: Filter by status (available, backfilled, expired)
        
        Returns:
            List of freed slots
        """
        slots = self._load_json(self.freed_slots_file)
        
        filtered = [s for s in slots if s.get("status", "").lower() == status.lower()]
        
        print(f"📅 Found {len(filtered)} {status} freed slots")
        return filtered
    
    def add_freed_slot(self, slot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add a freed appointment slot.
        
        Args:
            slot_data: Freed slot data
        
        Returns:
            Created slot with ID
        """
        slots = self._load_json(self.freed_slots_file)
        
        # Generate ID if not provided
        if "slot_id" not in slot_data:
            max_id = max([int(s["slot_id"].replace("SLOT", "")) for s in slots if "slot_id" in s], default=0)
            slot_data["slot_id"] = f"SLOT{max_id + 1:03d}"
        
        # Set default status
        if "status" not in slot_data:
            slot_data["status"] = "available"
        
        slots.append(slot_data)
        
        if self._save_json(self.freed_slots_file, slots):
            print(f"✅ Added freed slot: {slot_data['slot_id']}")
            return {"status": "SUCCESS", "slot": slot_data}
        else:
            return {"status": "ERROR", "message": "Failed to save freed slot"}
    
    def backfill_slot(self, slot_id: str, patient_id: str, appointment_id: str) -> bool:
        """Mark a freed slot as backfilled.
        
        Args:
            slot_id: Slot ID
            patient_id: Patient who filled the slot
            appointment_id: New appointment ID
        
        Returns:
            Success status
        """
        from datetime import datetime
        
        slots = self._load_json(self.freed_slots_file)
        
        for slot in slots:
            if slot.get("slot_id") == slot_id:
                slot["status"] = "backfilled"
                slot["backfilled_with"] = {
                    "patient_id": patient_id,
                    "appointment_id": appointment_id
                }
                slot["backfilled_at"] = datetime.utcnow().isoformat() + "Z"
                
                if self._save_json(self.freed_slots_file, slots):
                    print(f"✅ Backfilled slot {slot_id} with patient {patient_id}")
                    return True
        
        print(f"⚠️  Freed slot {slot_id} not found")
        return False


# Convenience function
def create_json_client(data_dir: str = None) -> JSONClient:
    """Create JSON client instance."""
    return JSONClient(data_dir=data_dir)


if __name__ == "__main__":
    # Test the client
    print("=== JSON CLIENT TEST ===\n")
    
    client = create_json_client()
    
    # Test 1: Get providers
    print("\n1. Testing get_all_providers:")
    providers = client.get_all_providers()
    if providers:
        print(f"   First provider: {providers[0].get('provider_id')} - {providers[0].get('name')}")
    
    # Test 2: Get appointments for provider
    print("\n2. Testing get_appointments_for_provider:")
    appointments = client.get_appointments_for_provider("T001")
    if appointments:
        print(f"   First appointment: {appointments[0].get('appointment_id')}")
        print(f"   Patient: {appointments[0].get('patient_id')}")
        print(f"   Date: {appointments[0].get('date')} at {appointments[0].get('time')}")
    
    # Test 3: Get patient
    print("\n3. Testing get_patient:")
    patient = client.get_patient("PAT001")
    if patient:
        print(f"   Patient: {patient.get('name')}")
        print(f"   Condition: {patient.get('condition')}")
    
    # Test 4: Get specific provider
    print("\n4. Testing get_provider:")
    provider = client.get_provider("P001")
    if provider:
        print(f"   Provider: {provider.get('name')}")
        print(f"   Specialty: {provider.get('specialty')}")
        print(f"   Status: {provider.get('status')}")
    
    print("\n✅ JSON client tests complete!")
    print("\n💡 To add more data, just edit the JSON files in data/ folder")

