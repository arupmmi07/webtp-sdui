"""Mock test data for thin slice demo.

This module contains hardcoded data for 1 patient, 3 providers, and 1 appointment
to test the complete workflow.

NOTE: This is MOCKED data. See MOCKS.md for how to swap to real database/API.
"""

from datetime import datetime, timedelta

# Mock Patient Data
MOCK_PATIENTS = {
    "PAT001": {
        "patient_id": "PAT001",
        "name": "Maria Rodriguez",
        "age": 55,
        "gender": "female",
        
        # Contact
        "phone": "+1-555-0123",
        "email": "maria.rodriguez@email.com",
        "address": "123 Main St, Metro City, CA 90001",
        
        # Clinical
        "condition": "post-surgical knee",
        "condition_specialty_required": "orthopedic",
        "chief_complaint": "Right knee pain and limited mobility 8 weeks post-op",
        "diagnosis_code": "M25.561",  # Pain in right knee
        
        # Insurance
        "insurance_type": "medicare",
        "insurance_plan": "Medicare Part B",
        "insurance_id": "1EG4-TE5-MK73",
        
        # POC (Plan of Care)
        "poc_active": True,
        "poc_expiration_date": "2024-12-15",
        "poc_approved_providers": ["P001", "P004", "P006"],  # Provider IDs authorized
        "poc_remaining_visits": 15,
        
        # History
        "total_appointments": 12,
        "completed_appointments": 10,
        "no_shows": 1,
        "no_show_rate": 0.08,  # 1/12 = 8%
        "no_show_risk": 0.2,  # Low risk
        "last_appointment_date": "2024-11-01",
        "prior_providers": ["T001", "P004"],  # Has seen Dr. Johnson (T001) and Dr. Lee (P004)
        
        # Preferences
        "gender_preference": "female",  # Prefers female therapist
        "preferred_days": ["tuesday", "thursday"],
        "preferred_time_block": "morning",  # 7-12 PM
        "max_distance_miles": 10.0,
        "communication_channel_primary": "sms",
        "communication_channel_secondary": "email",
        "telehealth_acceptable": False,
    }
}

# Mock Provider Data
MOCK_PROVIDERS = {
    "P001": {
        "provider_id": "P001",
        "name": "Dr. Emily Ross",
        "age": 38,
        "gender": "female",
        
        # Qualifications
        "specialty": "orthopedic",
        "certifications": ["Orthopedic PT", "Manual Therapy", "Board Certified"],
        "license_number": "PT-CA-12345",
        "license_active": True,
        "npi_number": "1234567890",
        "years_experience": 12,
        
        # Capacity
        "current_patient_load": 15,
        "max_patient_capacity": 25,
        "capacity_utilization": 0.60,  # 60%
        
        # Location & Availability
        "primary_location": "Metro PT Main Clinic",
        "location_address": "100 Health Plaza, Metro City, CA 90001",
        "distance_from_maria": 2.0,  # miles
        "available_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "available_slots": {
            "2024-11-20": ["10:00 AM", "2:00 PM"],  # Tuesday (Maria's preferred day!)
            "2024-11-21": ["9:00 AM", "11:00 AM"],
        },
        
        # Insurance
        "accepted_insurances": ["medicare", "ppo", "hmo"],
        "medicare_approved": True,
        
        # Other
        "email": "emily.ross@metropt.com",
        "phone": "+1-555-0201",
        "in_person_available": True,
        "telehealth_available": True,
    },
    
    "P004": {
        "provider_id": "P004",
        "name": "Dr. Michael Lee",
        "age": 45,
        "gender": "male",
        
        # Qualifications
        "specialty": "general",
        "certifications": ["General PT", "Orthopedic Training", "Sports Medicine"],
        "license_number": "PT-CA-54321",
        "license_active": True,
        "npi_number": "9876543210",
        "years_experience": 18,
        
        # Capacity
        "current_patient_load": 22,
        "max_patient_capacity": 25,
        "capacity_utilization": 0.88,  # 88% - near max!
        
        # Location & Availability
        "primary_location": "Metro PT Main Clinic",
        "location_address": "100 Health Plaza, Metro City, CA 90001",
        "distance_from_maria": 2.0,  # miles
        "available_days": ["monday", "tuesday", "thursday"],
        "available_slots": {
            "2024-11-21": ["3:00 PM"],  # Thursday afternoon (not Maria's preference)
        },
        
        # Insurance
        "accepted_insurances": ["medicare", "ppo", "workers_comp"],
        "medicare_approved": True,
        
        # Other
        "email": "michael.lee@metropt.com",
        "phone": "+1-555-0202",
        "in_person_available": True,
        "telehealth_available": False,
        
        # Special note
        "prior_patient_relationship": ["PAT001"],  # Treated Maria 2 years ago!
    },
    
    "P003": {
        "provider_id": "P003",
        "name": "Dr. Sarah Park",
        "age": 42,
        "gender": "female",
        
        # Qualifications
        "specialty": "orthopedic",
        "certifications": ["Orthopedic PT", "Sports Medicine"],
        "license_number": "PT-CA-98765",
        "license_active": True,
        "npi_number": "5555555555",
        "years_experience": 15,
        
        # Capacity
        "current_patient_load": 18,
        "max_patient_capacity": 25,
        "capacity_utilization": 0.72,  # 72%
        
        # Location & Availability
        "primary_location": "Metro PT East Clinic",
        "location_address": "500 East Ave, Metro City, CA 90015",
        "distance_from_maria": 15.0,  # miles - TOO FAR! (exceeds 10 mile limit)
        "available_days": ["monday", "tuesday", "wednesday", "friday"],
        "available_slots": {
            "2024-11-20": ["2:00 PM"],  # Tuesday afternoon
            "2024-11-22": ["10:00 AM"],
        },
        
        # Insurance
        "accepted_insurances": ["medicare", "ppo"],
        "medicare_approved": True,
        
        # Other
        "email": "sarah.park@metropt.com",
        "phone": "+1-555-0203",
        "in_person_available": True,
        "telehealth_available": True,
    },
}

# Mock Appointment Data
MOCK_APPOINTMENTS = {
    "A001": {
        "appointment_id": "A001",
        "patient_id": "PAT001",
        "original_provider_id": "T001",  # Dr. Johnson (departed)
        "original_provider_name": "Dr. Sarah Johnson",
        "date": "2024-11-20",  # Tuesday
        "time": "10:00 AM",
        "duration_minutes": 60,
        "status": "needs_reassignment",
        "condition": "post-surgical knee rehabilitation",
        "visit_number": 11,  # 11th visit out of POC
        "priority_score": 87,  # High priority (high no-show risk prevention)
    }
}

# Mock Therapist Departure Event
MOCK_DEPARTURE = {
    "therapist_id": "T001",
    "therapist_name": "Dr. Sarah Johnson",
    "departure_reason": "sick_leave",
    "departure_date": "2024-11-18",
    "return_date": "2024-12-02",  # Out for 2 weeks
    "affected_appointments": ["A001"],
    "notification_sent": True,
    "notification_time": "2024-11-18 09:00:00",
}

# Expected Demo Results (for testing/validation)
EXPECTED_DEMO_RESULTS = {
    "filtering": {
        "initial_candidates": ["P001", "P004", "P003"],
        "qualified_after_filtering": ["P001", "P004"],
        "eliminated": {
            "P003": "Location constraint: 15 miles exceeds 10 mile limit"
        }
    },
    "scoring": {
        "P001": {
            "total_score": 75,
            "breakdown": {
                "continuity": 0,  # Never seen Maria
                "specialty": 35,  # Perfect orthopedic match
                "preference_fit": 30,  # Female, same clinic
                "load_balance": 10,  # 60% capacity
                "day_time_match": 20,  # Tuesday 10 AM perfect match!
            },
            "rank": 1,
            "recommendation": "EXCELLENT"
        },
        "P004": {
            "total_score": 48,  # Below 50, but included for demo
            "breakdown": {
                "continuity": 40,  # Treated Maria 2 years ago
                "specialty": 25,  # General with orthopedic training
                "preference_fit": 5,  # Male (doesn't match), same clinic
                "load_balance": 3,  # 88% capacity (near max)
                "day_time_match": 5,  # Thursday PM (not preferred)
            },
            "rank": 2,
            "recommendation": "ACCEPTABLE (continuity)"
        }
    },
    "consent": {
        "offered_provider": "P001",
        "patient_response": "YES",
        "response_time_minutes": 45,
        "channel_used": "sms"
    },
    "booking": {
        "final_provider": "P001",
        "final_provider_name": "Dr. Emily Ross",
        "appointment_date": "2024-11-20",
        "appointment_time": "10:00 AM",
        "status": "CONFIRMED"
    }
}


def get_patient(patient_id: str):
    """Get patient by ID."""
    return MOCK_PATIENTS.get(patient_id)


def get_provider(provider_id: str):
    """Get provider by ID."""
    return MOCK_PROVIDERS.get(provider_id)


def get_appointment(appointment_id: str):
    """Get appointment by ID."""
    return MOCK_APPOINTMENTS.get(appointment_id)


def get_all_providers():
    """Get all providers."""
    return list(MOCK_PROVIDERS.values())


def get_affected_appointments(therapist_id: str):
    """Get appointments affected by therapist departure."""
    if therapist_id == "T001":
        return [MOCK_APPOINTMENTS["A001"]]
    return []


if __name__ == "__main__":
    # Quick test
    print("=== MOCK DATA TEST ===")
    print(f"Patient: {MOCK_PATIENTS['PAT001']['name']}")
    print(f"Providers: {len(MOCK_PROVIDERS)}")
    print(f"Appointments: {len(MOCK_APPOINTMENTS)}")
    print(f"\nExpected Winner: {EXPECTED_DEMO_RESULTS['scoring']['P001']['recommendation']}")
    print("✅ Mock data loaded successfully")




