"""Patient Engagement Agent.

Handles:
- Use Case 4: Automated Patient Offer Flow with Multi-Channel Communication

Uses real LLM by default (LM Studio or cloud API), with mock as fallback.
"""

from typing import Dict, Any, List
import sys
import os
import time as time_module
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.llm.base import BaseLLM
from adapters.llm.mock_llm import MockLLM
from mcp_servers.domain.json_server import JSONDomainServer, create_json_domain_server
from config.email_templates import EmailTemplates
from demo.email_preview import mock_send_email


# Import LiteLLM adapter if available
try:
    from adapters.llm.litellm_adapter import LiteLLMAdapter
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

# Import LangFuse if available
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False


class PatientEngagementAgent:
    """Patient Engagement Agent - handles patient communication and consent.
    
    This agent manages:
    - Multi-channel communication (SMS, Email, IVR)
    - Patient consent workflow
    - Response handling
    
    Uses real LLM by default for intelligent communication.
    Uses REAL JSON data for patient info.
    """
    
    def __init__(
        self,
        llm: BaseLLM = None,
        domain_server: JSONDomainServer = None
    ):
        """Initialize agent with service dependencies."""
        # Counter for AI-generated emails (limit to first 2 for demo speed)
        self.ai_email_count = 0
        self.max_ai_emails = 2  # Only generate AI for first 2 emails
        
        # Determine which LLM to use
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if llm:
            # Use provided LLM
            self.llm = llm
            llm_type = "Custom LLM"
        elif use_mock or not LITELLM_AVAILABLE:
            # Use Mock LLM
            self.llm = MockLLM()
            llm_type = "Mock LLM"
            if not use_mock:
                print(f"[AGENT] Warning: LiteLLM not available, using Mock LLM")
        else:
            # Use Real LLM via LiteLLM (if available)
            litellm_base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:1234/v1")
            litellm_api_key = os.getenv("LITELLM_API_KEY", "sk-1234")
            default_model = os.getenv("LITELLM_DEFAULT_MODEL", "gpt-oss-20b")
            
            try:
                self.llm = LiteLLMAdapter(
                    model=default_model,
                    api_base=litellm_base_url,
                    api_key=litellm_api_key,
                    enable_langfuse=False  # Disable LangFuse for simplicity
                )
                llm_type = f"Real LLM ({default_model})"
            except ImportError as e:
                print(f"[AGENT] Warning: LiteLLM not available - {e}")
                print(f"[AGENT] Falling back to Mock LLM")
                self.llm = MockLLM()
                llm_type = "Mock LLM (LiteLLM not installed)"
        
        self.domain = domain_server or create_json_domain_server()
        
        # Initialize LangFuse if available and enabled
        self.langfuse = None
        self.use_langfuse_prompt = os.getenv("USE_LANGFUSE_EMAIL_PROMPT", "true").lower() == "true"
        
        if self.use_langfuse_prompt and LANGFUSE_AVAILABLE:
            langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            langfuse_host = os.getenv("LANGFUSE_HOST") or os.getenv("LANGFUSE_BASE_URL") or "https://cloud.langfuse.com"
            
            if langfuse_public_key and langfuse_secret_key:
                try:
                    self.langfuse = Langfuse(
                        public_key=langfuse_public_key,
                        secret_key=langfuse_secret_key,
                        host=langfuse_host
                    )
                    print(f"[AGENT] LangFuse initialized for email personalization")
                except Exception as e:
                    print(f"[AGENT] Warning: LangFuse initialization failed: {e}")
                    self.langfuse = None
            else:
                print(f"[AGENT] Warning: LangFuse credentials not found, using template")
                self.use_langfuse_prompt = False
        
        print(f"\n[AGENT] Patient Engagement Agent initialized")
        print(f"[AGENT] LLM: {llm_type}")
        print(f"[AGENT] Domain: JSON-based (real data)")
        print(f"[AGENT] Email Personalization: {'LangFuse Prompt' if self.use_langfuse_prompt and self.langfuse else 'Template'}")
    
    def send_offer(
        self,
        patient_id: str,
        appointment_id: str,
        new_provider_id: str,
        date: str,
        time: str
    ) -> Dict[str, Any]:
        """
        UC4: Send offer to patient for new provider assignment.
        
        Args:
            patient_id: Patient ID
            appointment_id: Appointment ID
            new_provider_id: New provider ID being offered
            date: Appointment date
            time: Appointment time
            
        Returns:
            Dict with send status and message details
        """
        print(f"\n{'='*60}")
        print(f"[UC4: CONSENT] Sending offer to patient {patient_id}")
        print(f"{'='*60}")
        
        # Get patient and provider details
        patient = self.domain.get_patient(patient_id)
        provider = self.domain.get_provider(new_provider_id)
        
        if not patient or not provider:
            print(f"[UC4: CONSENT] ❌ Patient or provider not found")
            return {"status": "error", "message": "Patient or provider not found"}
        
        # Determine communication channel
        channel = patient.get("communication_channel_primary", "email")
        contact_info = patient.get("email") if channel == "email" else patient.get("phone")
        
        # Generate confirmation links
        from config.app_config import get_email_accept_url, get_email_decline_url
        token = f"{appointment_id}_{patient_id}_{new_provider_id}"
        accept_url = get_email_accept_url(token)
        decline_url = get_email_decline_url(token)
        
        # Send email(s) - AI for first 2, then template only
        print(f"[{channel.upper()} MOCK] Sending to {contact_info}")
        
        # 1. Generate AI message (only for first 2 emails for demo speed)
        ai_message = None
        should_generate_ai = (
            self.use_langfuse_prompt and 
            self.langfuse and 
            self.llm and 
            self.ai_email_count < self.max_ai_emails
        )
        
        if should_generate_ai:
            try:
                ai_message = self._compose_offer_message(
                    patient=patient,
                    provider=provider,
                    date=date,
                    time=time,
                    appointment_id=appointment_id,
                    use_ai=True
                )
                # Don't add links - buttons are displayed separately in emails.html
                
                print(f"[{channel.upper()} MOCK] 🤖 AI Message ({self.ai_email_count + 1}/{self.max_ai_emails}):\n{ai_message}")
                
                # Save AI email (message without links - buttons handled separately)
                self._save_email({
                    "id": f"{token}_ai",
                    "patient_id": patient_id,
                    "patient_name": patient.get("name", "Unknown"),
                    "patient_email": contact_info,
                    "appointment_id": appointment_id,
                    "provider_id": new_provider_id,
                    "provider_name": provider.get("name", "Unknown"),
                    "date": date,
                    "time": time,
                    "subject": f"New Provider Assignment - {provider.get('name')} (AI-Generated)",
                    "message": ai_message,  # Clean message without links
                    "accept_url": accept_url,  # URLs stored separately for buttons
                    "decline_url": decline_url,
                    "status": "pending",
                    "generation_type": "ai",
                    "sent_at": __import__('datetime').datetime.now().isoformat()
                })
                
                self.ai_email_count += 1  # Increment counter
                
            except Exception as e:
                print(f"[EMAIL] Warning: AI message generation failed: {e}")
        else:
            if self.ai_email_count >= self.max_ai_emails:
                print(f"[{channel.upper()} MOCK] ⏩ Skipping AI generation (limit reached: {self.max_ai_emails}), using template only")
        
        # 2. Generate Template message (always)
        template_message = self._compose_offer_message(
            patient=patient,
            provider=provider,
            date=date,
            time=time,
            appointment_id=appointment_id,
            use_ai=False
        )
        
        # Don't add links - buttons are displayed separately in emails.html
        # Just add a simple closing
        template_message_clean = f"""{template_message}

Thank you!
Metro Physical Therapy"""
        
        print(f"[{channel.upper()} MOCK] 📝 Template Message:\n{template_message_clean}")
        
        # Save Template email (message without links - buttons handled separately)
        self._save_email({
            "id": f"{token}_template",
            "patient_id": patient_id,
            "patient_name": patient.get("name", "Unknown"),
            "patient_email": contact_info,
            "appointment_id": appointment_id,
            "provider_id": new_provider_id,
            "provider_name": provider.get("name", "Unknown"),
            "date": date,
            "time": time,
            "subject": f"New Provider Assignment - {provider.get('name')} (Template)",
            "message": template_message_clean,  # Clean message without links
            "accept_url": accept_url,  # URLs stored separately for buttons
            "decline_url": decline_url,
            "status": "pending",
            "generation_type": "template",
            "sent_at": __import__('datetime').datetime.now().isoformat()
        })
        
        print(f"[{channel.upper()} MOCK] ✅ ACCEPT: {accept_url}")
        print(f"[{channel.upper()} MOCK] ❌ DECLINE: {decline_url}")
        print(f"[UC4: CONSENT] ✓ Offers sent via {channel.upper()} to {contact_info} (AI + Template)")
        
        # Return the template message as primary (for backward compatibility)
        return {
            "status": "sent",
            "channel": channel,
            "contact_info": contact_info,
            "message": template_message_clean,
            "ai_message": ai_message if ai_message else None,
            "confirmation_token": token,
            "accept_url": accept_url,
            "decline_url": decline_url
        }
    
    def _save_email(self, email_data: Dict[str, Any]) -> None:
        """Save email to JSON file for demo viewing."""
        import json
        from pathlib import Path
        
        emails_file = Path(__file__).parent.parent / "data" / "emails.json"
        
        try:
            # Load existing emails
            if emails_file.exists():
                with open(emails_file, 'r') as f:
                    emails = json.load(f)
            else:
                emails = []
            
            # Add new email
            emails.append(email_data)
            
            # Save back
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2)
                
            print(f"[EMAIL] Saved to {emails_file}")
        except Exception as e:
            print(f"[EMAIL] Warning: Failed to save email - {e}")
    
    def _compose_offer_message(
        self,
        patient: Dict[str, Any],
        provider: Dict[str, Any],
        date: str,
        time: str,
        appointment_id: str,
        use_ai: bool = False
    ) -> str:
        """Compose patient offer message using LangFuse prompt or template.
        
        Args:
            use_ai: If True, use AI (LangFuse prompt). If False, use template.
        """
        # Check if LangFuse prompt should be used
        if use_ai and self.use_langfuse_prompt and self.langfuse and self.llm:
            try:
                # Get original provider from appointment
                appointment = self.domain.get_appointment(appointment_id)
                original_provider_id = appointment.get('provider_id') if appointment else None
                original_provider = self.domain.get_provider(original_provider_id) if original_provider_id else None
                original_provider_name = original_provider.get('name', 'Your therapist') if original_provider else 'Your therapist'
                
                # Fetch prompt from LangFuse
                prompt_obj = self.langfuse.get_prompt(
                    "patient-engagement-message",
                    label="production"
                )
                
                # Compile prompt with comprehensive variables for better personalization
                compiled_prompt = prompt_obj.compile(
                    message_type="APPOINTMENT_OFFER",
                    patient_name=patient.get("name", "Patient"),
                    patient_condition=patient.get("condition", "N/A"),
                    patient_gender_preference=patient.get("gender_preference", "any"),
                    patient_preferred_days=patient.get("preferred_days", "any"),
                    patient_max_distance=f"{patient.get('max_distance_miles', 'N/A')} miles" if patient.get('max_distance_miles') else "N/A",
                    original_provider=original_provider_name,
                    new_provider=provider.get("name", "Provider"),
                    provider_specialty=provider.get("specialty", "Physical Therapy"),
                    provider_experience=str(provider.get("years_experience", "N/A")),
                    provider_available_days=", ".join(provider.get("available_days", [])),
                    appointment_date=date,
                    appointment_time=time,
                    location=provider.get("primary_location", "Main Clinic"),
                    channel=patient.get("communication_channel_primary", "email"),
                    match_reasoning="Provider matches patient's specialty requirements and preferences",
                    match_quality="EXCELLENT"  # Could be enhanced with actual match quality from appointment
                )
                
                # Call LLM with the compiled prompt
                print(f"[EMAIL] Calling LLM for personalized message...")
                system_prompt = """You are a healthcare communication assistant. Generate friendly, professional patient messages.

IMPORTANT: Do NOT include any links, URLs, or clickable buttons in your message. 
The links will be added separately after your message. Just provide the message content only."""
                
                response = self.llm.generate(
                    prompt=compiled_prompt,
                    system=system_prompt,
                    max_tokens=500,
                    temperature=0.7
                )
                
                # Extract message content
                llm_output = response.content if hasattr(response, 'content') else str(response)
                
                # Try to parse JSON response (if LLM returns structured format)
                import json
                try:
                    parsed = json.loads(llm_output.strip())
                    if isinstance(parsed, dict) and 'message' in parsed:
                        message = parsed['message']
                    elif isinstance(parsed, dict) and 'content' in parsed:
                        message = parsed['content']
                    else:
                        message = llm_output.strip()
                except (json.JSONDecodeError, AttributeError):
                    # If not JSON, use the raw output
                    message = llm_output.strip()
                
                print(f"[EMAIL] ✅ Using LLM-generated personalized message")
                return message
                
            except Exception as e:
                print(f"[EMAIL] Warning: LangFuse prompt/LLM call failed: {e}")
                import traceback
                traceback.print_exc()
                print(f"[EMAIL] Falling back to template")
                # Fall through to template
        
        # Use template (default or fallback)
        patient_name = patient.get("name", "Patient")
        provider_name = provider.get("name", "Provider")
        provider_specialty = provider.get("specialty", "Physical Therapy")
        
        message = f"""Hi {patient_name},

Your therapist has an unexpected absence. We'd like to reassign your appointment to:

👨‍⚕️ {provider_name}
📋 {provider_specialty}
📅 {date} at {time}

This provider is available and matches your needs based on your preferences.

Please let us know if this works for you. If you have any questions or concerns, please don't hesitate to reach out.

Thank you!
Metro Physical Therapy"""
        
        return message
    
    def send_confirmation(
        self,
        patient_id: str,
        appointment_id: str,
        provider_id: str,
        date: str,
        time: str
    ) -> Dict[str, Any]:
        """
        Send confirmation message after patient accepts.
        
        Args:
            patient_id: Patient ID
            appointment_id: Appointment ID
            provider_id: Confirmed provider ID
            date: Appointment date
            time: Appointment time
            
        Returns:
            Dict with send status
        """
        print(f"\n[UC4: CONFIRM] Sending confirmation to patient {patient_id}")
        
        # Get patient details
        patient = self.domain.get_patient(patient_id)
        provider = self.domain.get_provider(provider_id)
        
        # Determine communication channel
        channel = patient.get("communication_channel_primary", "email")
        contact_info = patient.get("email") if channel == "email" else patient.get("phone")
        
        # Compose confirmation message
        patient_name = patient.get("name", "Patient")
        provider_name = provider.get("name", "Provider")
        
        message = f"""Hi {patient_name},

✅ Your appointment is confirmed!

👨‍⚕️ Provider: {provider_name}
📅 Date: {date}
🕐 Time: {time}
🏥 Location: {provider.get("primary_location", "Main Clinic")}

Confirmation #: {appointment_id}

See you then!
"""
        
        # Send via appropriate channel (mocked for now)
        print(f"[{channel.upper()} MOCK] Sending to {contact_info}")
        print(f"[{channel.upper()} MOCK] Message:\n{message}")
        print(f"[UC4: CONFIRM] ✓ Confirmation sent via {channel.upper()} to {contact_info}")
        
        return {
            "status": "sent",
            "channel": channel,
            "contact_info": contact_info,
            "message": message
        }
    
    def handle_patient_response(
        self,
        token: str,
        response: str
    ) -> Dict[str, Any]:
        """
        Handle patient response to offer.
        
        Args:
            token: Unique token identifying the offer
            response: Patient response (yes/no/info)
            
        Returns:
            Dict with response handling result
        """
        print(f"\n[UC4: RESPONSE] Handling patient response: {response}")
        
        # For demo, just return the response
        # In production, this would update database, trigger workflows, etc.
        
        return {
            "status": "processed",
            "response": response,
            "token": token
        }
