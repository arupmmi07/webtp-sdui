"""Mock MCP Domain API Server.

This server exposes domain APIs (Patient, Provider, Appointment) via MCP protocol.
Currently MOCKED with hardcoded data from demo/mock_data.py.

See MOCKS.md for how to swap to real database/API.
"""

import sys
from pathlib import Path

# Add parent directory to path to import demo.mock_data
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from demo.mock_data import (
    MOCK_PATIENTS, MOCK_PROVIDERS, MOCK_APPOINTMENTS,
    MOCK_DEPARTURE, get_patient, get_provider, get_appointment,
    get_all_providers, get_affected_appointments
)


class MockDomainServer:
    """Mock implementation of MCP Domain API Server.
    
    Mimics real database/API calls but returns hardcoded data.
    Ready to swap with real backend connection.
    """
    
    def __init__(self):
        self.name = "domain-server"
        print(f"[MOCK MCP] Domain Server initialized (MOCKED)")
        print(f"[MOCK MCP] Loaded: {len(MOCK_PATIENTS)} patients, {len(MOCK_PROVIDERS)} providers")
    
    # ===== PATIENT API =====
    
    def get_patient(self, patient_id: str) -> dict:
        """Mock: Get patient details by ID.
        
        Args:
            patient_id: Patient identifier (e.g., "PAT001")
        
        Returns:
            Patient dictionary (MOCKED from demo/mock_data.py)
        """
        print(f"[MOCK MCP] get_patient(patient_id='{patient_id}')")
        
        patient = get_patient(patient_id)
        
        if not patient:
            return {"error": f"Patient {patient_id} not found (MOCKED)"}
        
        return patient
    
    def get_patient_preferences(self, patient_id: str) -> dict:
        """Mock: Get patient's preferences for provider matching.
        
        Returns just the preference subset of patient data.
        """
        print(f"[MOCK MCP] get_patient_preferences(patient_id='{patient_id}')")
        
        patient = get_patient(patient_id)
        
        if not patient:
            return {"error": f"Patient {patient_id} not found"}
        
        return {
            "patient_id": patient_id,
            "gender_preference": patient.get("gender_preference"),
            "preferred_days": patient.get("preferred_days", []),
            "preferred_time_block": patient.get("preferred_time_block"),
            "max_distance_miles": patient.get("max_distance_miles", 10.0),
            "communication_channel_primary": patient.get("communication_channel_primary", "sms"),
            "telehealth_acceptable": patient.get("telehealth_acceptable", False)
        }
    
    def get_patient_history(self, patient_id: str) -> dict:
        """Mock: Get patient's appointment history and no-show risk."""
        print(f"[MOCK MCP] get_patient_history(patient_id='{patient_id}')")
        
        patient = get_patient(patient_id)
        
        if not patient:
            return {"error": f"Patient {patient_id} not found"}
        
        return {
            "patient_id": patient_id,
            "total_appointments": patient.get("total_appointments", 0),
            "completed_appointments": patient.get("completed_appointments", 0),
            "no_shows": patient.get("no_shows", 0),
            "no_show_rate": patient.get("no_show_rate", 0.0),
            "no_show_risk": patient.get("no_show_risk", 0.0),
            "prior_providers": patient.get("prior_providers", []),
            "last_appointment_date": patient.get("last_appointment_date")
        }
    
    # ===== PROVIDER API =====
    
    def get_provider(self, provider_id: str) -> dict:
        """Mock: Get provider details by ID.
        
        Args:
            provider_id: Provider identifier (e.g., "P001")
        
        Returns:
            Provider dictionary (MOCKED)
        """
        print(f"[MOCK MCP] get_provider(provider_id='{provider_id}')")
        
        provider = get_provider(provider_id)
        
        if not provider:
            return {"error": f"Provider {provider_id} not found (MOCKED)"}
        
        return provider
    
    def get_all_providers(self) -> list:
        """Mock: Get all providers."""
        print(f"[MOCK MCP] get_all_providers()")
        return get_all_providers()
    
    def get_available_providers(self, date: str = None) -> list:
        """Mock: Get providers who have availability on a given date.
        
        Args:
            date: Date string (e.g., "2024-11-20")
        
        Returns:
            List of providers with available slots (MOCKED)
        """
        print(f"[MOCK MCP] get_available_providers(date='{date}')")
        
        # For mock: return all providers (in real system, check availability)
        providers = get_all_providers()
        
        if date:
            # Filter by those who have slots on that date
            available = []
            for provider in providers:
                slots = provider.get("available_slots", {})
                if date in slots and len(slots[date]) > 0:
                    available.append(provider)
            return available
        
        return providers
    
    def check_provider_capacity(self, provider_id: str) -> dict:
        """Mock: Check if provider has capacity for new patient."""
        print(f"[MOCK MCP] check_provider_capacity(provider_id='{provider_id}')")
        
        provider = get_provider(provider_id)
        
        if not provider:
            return {"error": f"Provider {provider_id} not found"}
        
        current = provider.get("current_patient_load", 0)
        max_capacity = provider.get("max_patient_capacity", 25)
        utilization = current / max_capacity if max_capacity > 0 else 1.0
        
        return {
            "provider_id": provider_id,
            "current_load": current,
            "max_capacity": max_capacity,
            "utilization": utilization,
            "has_capacity": current < max_capacity,
            "availability": "good" if utilization < 0.7 else "limited" if utilization < 0.9 else "full"
        }
    
    # ===== APPOINTMENT API =====
    
    def get_appointment(self, appointment_id: str) -> dict:
        """Mock: Get appointment details by ID."""
        print(f"[MOCK MCP] get_appointment(appointment_id='{appointment_id}')")
        
        appointment = get_appointment(appointment_id)
        
        if not appointment:
            return {"error": f"Appointment {appointment_id} not found (MOCKED)"}
        
        return appointment
    
    def get_appointments_for_provider(self, provider_id: str, status: str = None) -> list:
        """Mock: Get all appointments for a provider.
        
        Args:
            provider_id: Provider ID
            status: Filter by status (scheduled, completed, cancelled, needs_reassignment)
        """
        print(f"[MOCK MCP] get_appointments_for_provider(provider_id='{provider_id}', status='{status}')")
        
        # For mock: only return appointments for T001 (departed therapist)
        if provider_id == "T001":
            appointments = [MOCK_APPOINTMENTS["A001"]]
            if status:
                appointments = [a for a in appointments if a.get("status") == status]
            return appointments
        
        return []
    
    def book_appointment(self, appointment_data: dict) -> dict:
        """Mock: Book/update an appointment.
        
        Args:
            appointment_data: Appointment details including patient_id, provider_id, date, time
        
        Returns:
            Confirmation with appointment ID (MOCKED)
        """
        print(f"[MOCK MCP] book_appointment(data={appointment_data})")
        
        # Mock: Just return success
        return {
            "status": "SUCCESS",
            "appointment_id": appointment_data.get("appointment_id", "A001"),
            "patient_id": appointment_data.get("patient_id"),
            "provider_id": appointment_data.get("provider_id"),
            "date": appointment_data.get("date"),
            "time": appointment_data.get("time"),
            "confirmation_number": "CONF-2024-001",
            "message": "Appointment booked successfully (MOCKED)"
        }
    
    # ===== NOTIFICATION API =====
    
    def send_sms(self, phone: str, message: str) -> dict:
        """Mock: Send SMS notification.
        
        In real system, this would call Twilio.
        For mock, just print to console.
        """
        print(f"[MOCK MCP] send_sms(phone='{phone}')")
        print(f"[SMS MOCK] To: {phone}")
        print(f"[SMS MOCK] Message: {message}")
        
        return {
            "status": "SENT (MOCKED)",
            "phone": phone,
            "message_id": "MSG-MOCK-001",
            "note": "SMS not actually sent (see MOCKS.md)"
        }
    
    def send_email(self, email: str, subject: str, body: str) -> dict:
        """Mock: Send email notification.
        
        In real system, this would call SendGrid.
        For mock, just print to console.
        """
        print(f"[MOCK MCP] send_email(email='{email}')")
        print(f"[EMAIL MOCK] To: {email}")
        print(f"[EMAIL MOCK] Subject: {subject}")
        
        return {
            "status": "SENT (MOCKED)",
            "email": email,
            "message_id": "EMAIL-MOCK-001",
            "note": "Email not actually sent (see MOCKS.md)"
        }
    
    # ===== WORKFLOW API =====
    
    def get_therapist_departure(self, therapist_id: str) -> dict:
        """Mock: Get therapist departure information."""
        print(f"[MOCK MCP] get_therapist_departure(therapist_id='{therapist_id}')")
        
        if therapist_id == "T001":
            return MOCK_DEPARTURE
        
        return {"error": f"No departure record for {therapist_id}"}
    
    def get_affected_appointments(self, therapist_id: str) -> list:
        """Mock: Get appointments affected by therapist departure."""
        print(f"[MOCK MCP] get_affected_appointments(therapist_id='{therapist_id}')")
        return get_affected_appointments(therapist_id)


# Convenience functions
def create_domain_server() -> MockDomainServer:
    """Create and return a domain server instance."""
    return MockDomainServer()


if __name__ == "__main__":
    # Test the mock server
    print("=== MOCK MCP DOMAIN SERVER TEST ===\n")
    
    server = create_domain_server()
    
    # Test 1: Get patient
    print("\n1. Testing get_patient:")
    patient = server.get_patient("PAT001")
    print(f"  Patient: {patient['name']}, Age: {patient['age']}, Condition: {patient['condition']}")
    
    # Test 2: Get patient preferences
    print("\n2. Testing get_patient_preferences:")
    prefs = server.get_patient_preferences("PAT001")
    print(f"  Gender pref: {prefs['gender_preference']}, Max distance: {prefs['max_distance_miles']} miles")
    
    # Test 3: Get provider
    print("\n3. Testing get_provider:")
    provider = server.get_provider("P001")
    print(f"  Provider: {provider['name']}, Specialty: {provider['specialty']}")
    
    # Test 4: Check capacity
    print("\n4. Testing check_provider_capacity:")
    capacity = server.check_provider_capacity("P001")
    print(f"  Capacity: {capacity['current_load']}/{capacity['max_capacity']} ({capacity['availability']})")
    
    # Test 5: Get affected appointments
    print("\n5. Testing get_affected_appointments:")
    appointments = server.get_affected_appointments("T001")
    print(f"  Affected appointments: {len(appointments)}")
    if appointments:
        print(f"  First: {appointments[0]['appointment_id']} - {appointments[0]['patient_id']}")
    
    # Test 6: Mock SMS
    print("\n6. Testing send_sms (mock):")
    result = server.send_sms("+1-555-0123", "Test message")
    print(f"  Status: {result['status']}")
    
    # Test 7: Book appointment
    print("\n7. Testing book_appointment:")
    booking = server.book_appointment({
        "appointment_id": "A001",
        "patient_id": "PAT001",
        "provider_id": "P001",
        "date": "2024-11-20",
        "time": "10:00 AM"
    })
    print(f"  Status: {booking['status']}, Confirmation: {booking['confirmation_number']}")
    
    print("\n✅ Mock Domain Server tests complete")




