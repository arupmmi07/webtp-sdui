"""
Mock Domain API Server using JSON files.
Simulates WebPT and other external systems.
"""
import json
import os
from typing import Dict, List, Optional
from api.json_client import JSONClient

class JSONDomainServer:
    """JSON-based Domain Server for patient, provider, and appointment data."""
    
    def __init__(self):
        self.json_client = JSONClient()
        print("✅ JSONDomainServer initialized (using JSON data)")
    
    def get_patient(self, patient_id: str) -> Optional[Dict]:
        """Get a single patient by ID."""
        return self.json_client.get_patient(patient_id)
    
    def get_provider(self, provider_id: str) -> Optional[Dict]:
        """Get a single provider by ID."""
        return self.json_client.get_provider(provider_id)
    
    def get_appointment(self, appointment_id: str) -> Optional[Dict]:
        """Get a single appointment by ID."""
        return self.json_client.get_appointment(appointment_id)
    
    def get_appointments_for_provider(self, provider_id: str) -> List[Dict]:
        """Get all appointments for a specific provider."""
        all_appointments = self.json_client._load_json(self.json_client.appointments_file)
        return [a for a in all_appointments if a.get("provider_id") == provider_id]
    
    def get_affected_appointments(self, provider_id: str) -> List[Dict]:
        """Get all affected appointments for a departing provider (alias for get_appointments_for_provider)."""
        return self.get_appointments_for_provider(provider_id)
    
    def get_available_providers(self, specialty: Optional[str] = None) -> List[Dict]:
        """Get all active providers, optionally filtered by specialty."""
        all_providers = self.json_client._load_json(self.json_client.providers_file)
        providers = [p for p in all_providers if p.get("status") == "active"]
        
        if specialty:
            providers = [p for p in providers if p.get("specialty") == specialty]
        
        return providers
    
    def update_appointment(self, appointment_id: str, updates: Dict) -> bool:
        """Update an appointment."""
        return self.json_client.update_appointment(appointment_id, updates)
    
    def book_appointment(self, appointment_data: Dict) -> Dict:
        """Book/update an appointment - now actually updates the JSON data!"""
        try:
            appointment_id = appointment_data.get("appointment_id")
            new_provider_id = appointment_data.get("provider_id")
            
            # Update the appointment in JSON
            success = self.json_client.reassign_appointment(
                appointment_id=appointment_id,
                new_provider_id=new_provider_id,
                reason="Provider reassignment"
            )
            
            if success:
                print(f"✅ Appointment {appointment_id} reassigned to {new_provider_id}")
                return {
                    "success": True,
                    "status": "SUCCESS",
                    "appointment_id": appointment_id,
                    "provider_id": new_provider_id,
                    "date": appointment_data.get("date"),
                    "time": appointment_data.get("time"),
                    "confirmation_number": f"CONF-{appointment_id[-3:]}-{new_provider_id[-3:]}",
                    "message": "Appointment reassigned successfully"
                }
            else:
                return {
                    "success": False,
                    "status": "ERROR",
                    "message": "Failed to reassign appointment"
                }
        except Exception as e:
            print(f"❌ Error booking appointment: {e}")
            return {
                "success": False,
                "status": "ERROR",
                "message": str(e)
            }
    
    def send_email(self, to: str, subject: str, body: str, response_url: Optional[str] = None) -> Dict:
        """Mock email sending."""
        print(f"\n📧 EMAIL SENT")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print(f"Body: {body[:100]}...")
        if response_url:
            print(f"Response URL: {response_url}")
        
        return {
            "success": True,
            "message": "Email sent",
            "to": to
        }
    
    def add_to_waitlist(self, waitlist_entry: Dict) -> Dict:
        """Add patient to waitlist."""
        return self.json_client.add_to_waitlist(waitlist_entry)
    
    def calculate_distance_between_zips(self, zip1: str, zip2: str) -> float:
        """
        Calculate distance between two zip codes.
        
        In a real system, this would call a geocoding API like:
        - Google Maps Distance Matrix API
        - Mapbox Distance API
        - Here.com Routing API
        
        For demo, we use a simple approximation based on zip code proximity.
        """
        # Simple heuristic: Calculate numeric distance between zips
        # In reality, you'd call an external API
        try:
            z1 = int(zip1)
            z2 = int(zip2)
            zip_diff = abs(z1 - z2)
            
            # Rough approximation: 1 zip unit ≈ 2 miles
            # This is a VERY rough estimate for demo purposes
            estimated_distance = zip_diff * 2.0
            
            # Add some variance to make it realistic
            if zip_diff == 0:
                return 0.0
            elif zip_diff <= 5:
                return min(estimated_distance, 5.0)
            elif zip_diff <= 10:
                return min(estimated_distance, 12.0)
            else:
                return min(estimated_distance, 15.0)
        except:
            # If zips can't be parsed as numbers, return a default
            return 10.0


def create_json_domain_server():
    """Factory function to create JSON domain server."""
    return JSONDomainServer()
