"""Patient Engagement Agent.

Handles:
- Use Case 4: Automated Patient Offer Flow with Multi-Channel Communication

Uses mocked services (mock SMS/email) that can be swapped later.
"""

from typing import Dict, Any
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.llm.mock_llm import MockLLM
from mcp_servers.domain.server import MockDomainServer


class PatientEngagementAgent:
    """Patient Engagement Agent - handles patient communication and consent.
    
    This agent manages:
    - Multi-channel communication (SMS, Email, IVR)
    - Patient consent workflow
    - Response handling
    
    Uses mocked communication (prints to console instead of real SMS/email).
    See MOCKS.md for how to swap to real Twilio/SendGrid.
    """
    
    def __init__(
        self,
        llm: MockLLM = None,
        domain_server: MockDomainServer = None
    ):
        """Initialize agent with service dependencies."""
        self.llm = llm or MockLLM()
        self.domain = domain_server or MockDomainServer()
        
        print(f"\n[AGENT] Patient Engagement Agent initialized")
        print(f"[AGENT] Using: Mock communication (no real SMS/email sent)")
    
    def send_offer(
        self,
        patient_id: str,
        provider_id: str,
        appointment: Dict[str, Any],
        original_provider_name: str = "your original therapist"
    ) -> Dict[str, Any]:
        """Use Case 4: Send appointment offer to patient and get consent.
        
        Args:
            patient_id: Patient ID
            provider_id: New provider ID being offered
            appointment: Appointment details
            original_provider_name: Name of departed therapist
        
        Returns:
            Consent result with patient response
        """
        print(f"\n{'='*60}")
        print(f"[UC4: CONSENT] Sending offer to patient {patient_id}")
        print(f"{'='*60}")
        
        # Get patient and provider details
        patient = self.domain.get_patient(patient_id)
        provider = self.domain.get_provider(provider_id)
        
        patient_name = patient['name']
        provider_name = provider['name']
        apt_date = appointment.get('date')
        apt_time = appointment.get('time')
        
        print(f"[UC4: CONSENT] Patient: {patient_name}")
        print(f"[UC4: CONSENT] Original Provider: {original_provider_name}")
        print(f"[UC4: CONSENT] New Provider: {provider_name}")
        print(f"[UC4: CONSENT] Appointment: {apt_date} at {apt_time}")
        
        # Get patient's communication preferences
        prefs = self.domain.get_patient_preferences(patient_id)
        primary_channel = prefs.get('communication_channel_primary', 'sms')
        
        print(f"[UC4: CONSENT] Preferred channel: {primary_channel.upper()}")
        
        # Compose message using LLM (or use template)
        message = self._compose_offer_message(
            patient_name=patient_name,
            original_provider_name=original_provider_name,
            new_provider_name=provider_name,
            date=apt_date,
            time=apt_time
        )
        
        # Send via appropriate channel (MOCKED)
        if primary_channel == 'sms':
            send_result = self._send_sms(patient['phone'], message)
        elif primary_channel == 'email':
            send_result = self._send_email(patient['email'], "Appointment Rescheduling", message)
        else:
            send_result = self._send_sms(patient['phone'], message)  # Default to SMS
        
        # Mock: Patient response (always YES for thin slice demo)
        # Real system would wait for actual patient response
        patient_response = "YES"
        response_time_minutes = 45  # Mock response time
        
        print(f"\n[UC4: CONSENT] ✓ Offer sent via {primary_channel.upper()}")
        print(f"[UC4: CONSENT] Patient response: {patient_response} (after {response_time_minutes} minutes)")
        
        return {
            "patient_id": patient_id,
            "provider_id": provider_id,
            "message_sent": message,
            "channel_used": primary_channel,
            "send_status": send_result['status'],
            "patient_response": patient_response,
            "response_time_minutes": response_time_minutes,
            "consent_granted": patient_response == "YES",
            "note": "MOCKED - Real system would wait for actual SMS/email response"
        }
    
    def _compose_offer_message(
        self,
        patient_name: str,
        original_provider_name: str,
        new_provider_name: str,
        date: str,
        time: str
    ) -> str:
        """Compose patient offer message.
        
        Uses simple template for now. Real system could use LLM for personalization.
        """
        message = f"""Hi {patient_name.split()[0]}, 

{original_provider_name} is unavailable. We can reschedule you with {new_provider_name} on {date} at {time}.

Reply YES to confirm, NO to decline, or INFO for more details about {new_provider_name}.

- Metro PT"""
        
        return message
    
    def _send_sms(self, phone: str, message: str) -> Dict[str, Any]:
        """Mock: Send SMS via Twilio.
        
        MOCKED: Just prints to console instead of sending real SMS.
        See MOCKS.md for how to swap to real Twilio.
        """
        print(f"\n[SMS MOCK] ==================")
        print(f"[SMS MOCK] To: {phone}")
        print(f"[SMS MOCK] Message:")
        print(f"[SMS MOCK] ---")
        for line in message.split('\n'):
            print(f"[SMS MOCK] {line}")
        print(f"[SMS MOCK] ==================")
        
        return self.domain.send_sms(phone, message)
    
    def _send_email(self, email: str, subject: str, body: str) -> Dict[str, Any]:
        """Mock: Send email via SendGrid.
        
        MOCKED: Just prints to console instead of sending real email.
        See MOCKS.md for how to swap to real SendGrid.
        """
        print(f"\n[EMAIL MOCK] ==================")
        print(f"[EMAIL MOCK] To: {email}")
        print(f"[EMAIL MOCK] Subject: {subject}")
        print(f"[EMAIL MOCK] Body:")
        print(f"[EMAIL MOCK] ---")
        for line in body.split('\n'):
            print(f"[EMAIL MOCK] {line}")
        print(f"[EMAIL MOCK] ==================")
        
        return self.domain.send_email(email, subject, body)
    
    def send_confirmation(
        self,
        patient_id: str,
        provider_id: str,
        appointment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Send confirmation after booking is complete.
        
        Args:
            patient_id: Patient ID
            provider_id: Booked provider ID
            appointment: Final appointment details
        
        Returns:
            Confirmation send result
        """
        print(f"\n[UC4: CONFIRM] Sending confirmation to {patient_id}")
        
        patient = self.domain.get_patient(patient_id)
        provider = self.domain.get_provider(provider_id)
        
        message = f"""Confirmed! Your appointment with {provider['name']} is scheduled for {appointment['date']} at {appointment['time']} at {provider['primary_location']}.

Reply CANCEL if you need to reschedule.

- Metro PT"""
        
        # Send confirmation
        channel = patient.get('communication_channel_primary', 'sms')
        if channel == 'sms':
            result = self._send_sms(patient['phone'], message)
        else:
            result = self._send_email(patient['email'], "Appointment Confirmed", message)
        
        print(f"[UC4: CONFIRM] ✓ Confirmation sent via {channel.upper()}")
        
        return {
            "patient_id": patient_id,
            "confirmation_sent": True,
            "channel": channel,
            "status": result['status']
        }


# Convenience function
def create_patient_engagement_agent() -> PatientEngagementAgent:
    """Create and return a Patient Engagement Agent instance."""
    return PatientEngagementAgent()


if __name__ == "__main__":
    # Test the agent
    print("=== PATIENT ENGAGEMENT AGENT TEST ===\n")
    
    agent = create_patient_engagement_agent()
    
    # Test: Send offer
    print("\n" + "="*70)
    print("TEST: Send Offer")
    print("="*70)
    
    appointment = {
        "appointment_id": "A001",
        "patient_id": "PAT001",
        "date": "2024-11-20",
        "time": "10:00 AM"
    }
    
    result = agent.send_offer(
        patient_id="PAT001",
        provider_id="P001",
        appointment=appointment,
        original_provider_name="Dr. Sarah Johnson"
    )
    
    print(f"\n✓ Offer sent: {result['send_status']}")
    print(f"✓ Patient response: {result['patient_response']}")
    print(f"✓ Consent granted: {result['consent_granted']}")
    
    if result['consent_granted']:
        # Test: Send confirmation
        print("\n" + "="*70)
        print("TEST: Send Confirmation")
        print("="*70)
        
        confirm_result = agent.send_confirmation(
            patient_id="PAT001",
            provider_id="P001",
            appointment=appointment
        )
        
        print(f"\n✓ Confirmation sent: {confirm_result['confirmation_sent']}")
    
    print("\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)




