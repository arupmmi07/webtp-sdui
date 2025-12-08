"""Unified web server with HTML pages + API endpoints.

Combines the web UI and API into a single server for simplified deployment.
Serves both HTML pages and provides all necessary API endpoints.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from pathlib import Path
import os
import json
from datetime import datetime, timedelta
import random
import sys

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[WEB_SERVER] Loaded .env from {env_path}")
        
        # Check Langfuse configuration
        if os.getenv('LANGFUSE_PUBLIC_KEY') and os.getenv('LANGFUSE_SECRET_KEY'):
            print("[WEB_SERVER] ✅ Langfuse credentials loaded")
            
            # Initialize Langfuse tracing
            try:
                from langfuse import Langfuse
                langfuse = Langfuse()
                print("[WEB_SERVER] ✅ Langfuse client initialized")
            except Exception as e:
                print(f"[WEB_SERVER] ⚠️  Langfuse initialization failed: {e}")
        else:
            print("[WEB_SERVER] ⚠️  Langfuse credentials not found in .env")
except ImportError:
    print("[WEB_SERVER] Warning: python-dotenv not installed. Run: pip install python-dotenv")

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from demo.email_preview import mock_send_email
from config.email_templates import EmailTemplates
from config.llm_settings import LLMSettings

# Create FastAPI app
app = FastAPI(
    title="WebTP Demo - Unified Server",
    description="""
    Unified web server with HTML pages and API endpoints.
    
    ## Features
    - Interactive HTML pages (schedule, emails, reset)
    - Complete REST API for appointments, providers, patients
    - Demo data management
    - Real-time scheduling operations
    
    ## Pages
    - **Schedule**: Interactive appointment calendar
    - **Emails**: Patient communication viewer
    - **Reset**: Demo data control panel
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Data Models
class TimeSlot(BaseModel):
    time: str
    date: Optional[str] = None
    available: Optional[bool] = True

class Provider(BaseModel):
    model_config = {"extra": "allow"}
    
    provider_id: str
    name: str
    specialty: Optional[str] = None
    gender: Optional[str] = None
    primary_location: Optional[str] = None
    zip: Optional[str] = None
    years_experience: Optional[int] = None
    experience_level: Optional[str] = None
    certifications: Optional[List[str]] = []
    available_days: Optional[List[str]] = []
    unavailable_dates: Optional[List[str]] = []
    working_hours_start: Optional[str] = "08:00"
    working_hours_end: Optional[str] = "17:00"
    available_slots: Optional[List[TimeSlot]] = []
    max_patient_capacity: Optional[int] = 50
    current_patient_load: Optional[int] = 0
    status: Optional[str] = "active"

class Appointment(BaseModel):
    model_config = {"extra": "allow"}
    
    appointment_id: str
    patient_id: str
    provider_id: str
    date: str
    time: str
    status: Optional[str] = "scheduled"
    confirmation_number: Optional[str] = None
    confirmation_status: Optional[str] = None
    reassigned: Optional[bool] = False
    original_provider_id: Optional[str] = None

class Patient(BaseModel):
    model_config = {"extra": "allow"}
    
    patient_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    condition: Optional[str] = None
    preferred_provider_gender: Optional[str] = None
    preferred_days: Optional[Any] = None  # Can be string or list
    max_distance_miles: Optional[float] = None

class DemoResetRequest(BaseModel):
    days_ahead: int = 5
    appointments_per_day: int = 3
    admin_key: str = None  # Required for admin operations

# Data directory
DATA_DIR = Path(__file__).parent / "data"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get paths
current_dir = Path(__file__).parent
static_dir = current_dir / "static"

# Mount static files
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ============================================================
# API Endpoints
# ============================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "WebTP Demo is running"}

@app.get("/confirm")
async def confirm_appointment(token: str, action: str = "accept"):
    """Handle appointment confirmation or decline."""
    try:
        # Load appointments
        appointments_file = DATA_DIR / "appointments.json"
        if not appointments_file.exists():
            raise HTTPException(status_code=404, detail="No appointments found")
        
        with open(appointments_file, 'r') as f:
            appointments = json.load(f)
        
        # Find appointment by token (appointment_id)
        appointment = None
        for apt in appointments:
            if apt.get('appointment_id') == token:
                appointment = apt
                break
        
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        
        # Load emails to update status
        emails_file = DATA_DIR / "emails.json"
        emails = []
        if emails_file.exists():
            with open(emails_file, 'r') as f:
                emails = json.load(f)
        
        # Update appointment and email status based on action
        if action == "accept":
            appointment['confirmation_status'] = "confirmed"
            appointment['status'] = "confirmed"
            
            # Update corresponding email status
            for email in emails:
                if email.get('appointment_id') == token:
                    email['status'] = "accepted"
                    break
            
            message = f"✅ Appointment {token} confirmed successfully!"
            
        elif action == "decline":
            appointment['confirmation_status'] = "declined"
            appointment['status'] = "cancelled"
            
            # Update corresponding email status
            for email in emails:
                if email.get('appointment_id') == token:
                    email['status'] = "declined"
                    break
            
            message = f"❌ Appointment {token} declined. We'll help you reschedule."
            
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'accept' or 'decline'")
        
        # Save updated appointments
        with open(appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        # Save updated emails
        if emails:
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2)
        
        # Return a simple HTML response
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Appointment Confirmation</title>
            <style>
                body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
                .success {{ color: #27ae60; font-size: 24px; margin-bottom: 20px; }}
                .decline {{ color: #e74c3c; font-size: 24px; margin-bottom: 20px; }}
                .details {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #007bff; color: white; text-decoration: none; border-radius: 6px; margin: 10px; }}
            </style>
        </head>
        <body>
            <div class="{'success' if action == 'accept' else 'decline'}">
                {message}
            </div>
            <div class="details">
                <h3>Appointment Details</h3>
                <p><strong>Appointment ID:</strong> {token}</p>
                <p><strong>Date:</strong> {appointment.get('date', 'N/A')}</p>
                <p><strong>Time:</strong> {appointment.get('time', 'N/A')}</p>
                <p><strong>Provider:</strong> {appointment.get('provider_name', 'N/A')}</p>
                <p><strong>Status:</strong> {appointment.get('confirmation_status', 'N/A').title()}</p>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        print(f"Confirmation error: {e}")
        raise HTTPException(status_code=500, detail=f"Confirmation failed: {str(e)}")

@app.get("/api/appointments")
async def get_appointments(
    provider_id: Optional[str] = Query(None, description="Filter by provider ID")
):
    """Get all appointments, optionally filtered by provider."""
    try:
        appointments_file = DATA_DIR / "appointments.json"
        if not appointments_file.exists():
            return []
        
        with open(appointments_file, 'r') as f:
            appointments = json.load(f)
        
        if provider_id:
            appointments = [apt for apt in appointments if apt.get('provider_id') == provider_id]
        
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading appointments: {str(e)}")

@app.get("/api/providers")
async def get_providers():
    """Get all healthcare providers."""
    try:
        providers_file = DATA_DIR / "providers.json"
        if not providers_file.exists():
            return []
        
        with open(providers_file, 'r') as f:
            providers = json.load(f)
        
        # Remove "Dr." prefix from names for UI consistency
        for provider in providers:
            if provider.get('name', '').startswith('Dr. '):
                provider['name'] = provider['name'][4:]  # Remove "Dr. "
        
        return providers
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading providers: {str(e)}")

@app.get("/api/patients")
async def get_patients():
    """Get all patients."""
    try:
        patients_file = DATA_DIR / "patients.json"
        if not patients_file.exists():
            return []
        
        with open(patients_file, 'r') as f:
            patients = json.load(f)
        
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading patients: {str(e)}")

@app.get("/api/emails")
async def get_emails():
    """Get sent emails."""
    try:
        emails_file = DATA_DIR / "emails.json"
        if not emails_file.exists():
            return []
        
        with open(emails_file, 'r') as f:
            emails = json.load(f)
        
        return emails
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading emails: {str(e)}")

@app.get("/api/waitlist")
async def get_waitlist():
    """Get waitlist entries."""
    try:
        waitlist_file = DATA_DIR / "waitlist.json"
        if not waitlist_file.exists():
            return []
        
        with open(waitlist_file, 'r') as f:
            waitlist = json.load(f)
        
        return waitlist
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading waitlist: {str(e)}")

@app.get("/api/freed-slots")
async def get_freed_slots():
    """Get freed appointment slots."""
    try:
        freed_slots_file = DATA_DIR / "freed_slots.json"
        if not freed_slots_file.exists():
            return []
        
        with open(freed_slots_file, 'r') as f:
            freed_slots = json.load(f)
        
        return freed_slots
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading freed slots: {str(e)}")

class ProviderUnavailableRequest(BaseModel):
    trigger_type: str
    provider_id: str
    reason: str
    start_date: str
    end_date: str
    metadata: Optional[dict] = None

@app.post("/api/trigger-workflow")
async def trigger_workflow(request: ProviderUnavailableRequest):
    """Simple provider unavailable handler - updates provider status only."""
    try:
        if request.trigger_type != "provider_unavailable":
            raise HTTPException(status_code=400, detail="Only provider_unavailable trigger type supported")
        
        # Load providers
        providers_file = DATA_DIR / "providers.json"
        with open(providers_file, 'r') as f:
            providers = json.load(f)
        
        # Find and update the provider
        provider_found = False
        for provider in providers:
            if provider.get("provider_id") == request.provider_id:
                provider_found = True
                
                # Update provider status based on reason
                if request.reason == "left_organization":
                    provider["status"] = "left_organization"
                    provider["unavailable_dates"] = []  # Clear specific dates since permanently unavailable
                else:
                    provider["status"] = "active"  # Keep active but add unavailable dates
                    
                    # Add dates to unavailable_dates
                    if "unavailable_dates" not in provider:
                        provider["unavailable_dates"] = []
                    
                    # Generate date range
                    start_dt = datetime.strptime(request.start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(request.end_date, "%Y-%m-%d")
                    
                    current = start_dt
                    while current <= end_dt:
                        date_str = current.strftime("%Y-%m-%d")
                        if date_str not in provider["unavailable_dates"]:
                            provider["unavailable_dates"].append(date_str)
                        current += timedelta(days=1)
                break
        
        if not provider_found:
            raise HTTPException(status_code=404, detail=f"Provider {request.provider_id} not found")
        
        # Save updated providers
        with open(providers_file, 'w') as f:
            json.dump(providers, f, indent=2)
        
        # Smart rescheduling logic based on unavailability duration
        appointments_file = DATA_DIR / "appointments.json"
        patients_file = DATA_DIR / "patients.json"
        
        with open(appointments_file, 'r') as f:
            appointments = json.load(f)
        with open(patients_file, 'r') as f:
            patients_data = json.load(f)
        
        # Create patient lookup
        patients_lookup = {p['patient_id']: p for p in patients_data}
        
        # Calculate unavailability duration
        start_dt = datetime.strptime(request.start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(request.end_date, "%Y-%m-%d").date()
        unavailable_days = (end_dt - start_dt).days + 1
        
        affected_appointments = []
        rescheduled_appointments = []
        waitlisted_appointments = []
        
        # Find affected appointments
        for appointment in appointments:
            if appointment.get("provider_id") == request.provider_id and appointment.get('status') == 'scheduled':
                apt_date_str = appointment.get('date', '').split('T')[0]
                
                should_reschedule = False
                if request.reason == "left_organization":
                    # Reschedule all future appointments for providers who left
                    try:
                        apt_date = datetime.strptime(apt_date_str, "%Y-%m-%d").date()
                        today = datetime.now().date()
                        if apt_date >= today:
                            should_reschedule = True
                    except:
                        pass
                else:
                    # Reschedule appointments on unavailable dates
                    if request.start_date <= apt_date_str <= request.end_date:
                        should_reschedule = True
                
                if should_reschedule:
                    affected_appointments.append(appointment)
        
        # Separate appointments by rescheduling strategy
        short_term_appointments = []
        long_term_appointments = []
        
        for appointment in affected_appointments:
            patient_id = appointment.get('patient_id')
            patient = patients_lookup.get(patient_id, {})
            
            if unavailable_days <= 2 and request.reason != "left_organization":
                short_term_appointments.append((appointment, patient))
            else:
                long_term_appointments.append((appointment, patient))
        
        # Handle short-term appointments (same provider logic)
        for appointment, patient in short_term_appointments:
            patient_id = appointment.get('patient_id')
            success = _reschedule_same_provider(appointment, request.provider_id, end_dt, appointments, providers)
            if success:
                # Send rescheduling email
                old_provider = next((p for p in providers if p['provider_id'] == request.provider_id), {})
                new_provider = old_provider  # Same provider, different date
                _send_rescheduling_email(appointment, patient, old_provider, new_provider, request.reason)
                
                rescheduled_appointments.append({
                    'appointment_id': appointment.get('appointment_id'),
                    'patient_id': patient_id,
                    'original_date': appointment.get('date'),
                    'new_provider_id': request.provider_id,  # Same provider
                    'new_date': appointment.get('date'),  # Updated by reschedule function
                    'reschedule_type': 'same_provider_next_day'
                })
            else:
                # Add to waitlist if no slots available with same provider
                _add_to_waitlist(appointment, patient, "No available slots with same provider")
                waitlisted_appointments.append({
                    'appointment_id': appointment.get('appointment_id'),
                    'patient_id': patient_id,
                    'reason': 'No slots available with same provider'
                })
        
        # Handle long-term appointments with BATCHED LLM call
        if long_term_appointments:
            provider_matches = _batch_provider_matching_with_llm(long_term_appointments, request.provider_id, providers)
            
            for i, (appointment, patient) in enumerate(long_term_appointments):
                patient_id = appointment.get('patient_id')
                new_provider = provider_matches.get(i) if provider_matches else None
                
                if new_provider:
                    # Try to reschedule with new provider
                    success = _reschedule_different_provider(appointment, new_provider['provider_id'], appointments)
                    if success:
                        # Send rescheduling email
                        old_provider = next((p for p in providers if p['provider_id'] == request.provider_id), {})
                        actual_new_provider = next((p for p in providers if p['provider_id'] == new_provider['provider_id']), {})
                        _send_rescheduling_email(appointment, patient, old_provider, actual_new_provider, request.reason)
                        
                        rescheduled_appointments.append({
                            'appointment_id': appointment.get('appointment_id'),
                            'patient_id': patient_id,
                            'original_date': appointment.get('date'),
                            'new_provider_id': new_provider['provider_id'],
                            'new_provider_name': new_provider.get('name'),
                            'new_date': appointment.get('date'),  # Updated by reschedule function
                            'reschedule_type': 'different_provider_match',
                            'match_factors': new_provider.get('llm_match_factors', {}),
                            'llm_reasoning': new_provider.get('llm_reasoning', '')
                        })
                    else:
                        # Add to waitlist if no slots available with new provider
                        _add_to_waitlist(appointment, patient, f"No available slots with matched provider {new_provider.get('name')}")
                        waitlisted_appointments.append({
                            'appointment_id': appointment.get('appointment_id'),
                            'patient_id': patient_id,
                            'reason': f"No slots with matched provider {new_provider.get('name')}"
                        })
                else:
                    # No suitable provider found - add to waitlist
                    _add_to_waitlist(appointment, patient, "No suitable provider match found")
                    waitlisted_appointments.append({
                        'appointment_id': appointment.get('appointment_id'),
                        'patient_id': patient_id,
                        'reason': 'No suitable provider match found'
                    })
        
        # Save updated appointments
        with open(appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        # Return success response with rescheduling details
        return {
            "success": True,
            "workflow_type": "provider_unavailable (SMART_RESCHEDULING)",
            "assignment_method": "duration-based-logic",
            "used_fallback": False,
            "provider_id": request.provider_id,
            "affected_appointments_count": len(affected_appointments),
            "rescheduled_count": len(rescheduled_appointments),
            "waitlisted_count": len(waitlisted_appointments),
            "unavailable_days": unavailable_days,
            "rescheduling_strategy": "same_provider_next_day" if unavailable_days <= 2 else "different_provider_match",
            "assignments": rescheduled_appointments,
            "emails_sent": len(rescheduled_appointments),  # Actual emails sent for rescheduled appointments
            "waitlist_count": len(waitlisted_appointments),
            "rescheduled_appointments": rescheduled_appointments,
            "waitlisted_appointments": waitlisted_appointments,
            "message": f"Provider {request.provider_id} unavailable for {unavailable_days} days - {len(rescheduled_appointments)} rescheduled, {len(waitlisted_appointments)} waitlisted",
            "details": {
                "strategy": f"{'Same provider next available day' if unavailable_days <= 2 else 'Match to different provider based on preferences'}",
                "rescheduled_appointments": rescheduled_appointments,
                "waitlisted_appointments": waitlisted_appointments
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating provider status: {str(e)}")

# Helper functions for smart rescheduling
def _reschedule_same_provider(appointment, provider_id, unavailable_end_date, appointments, providers):
    """Try to reschedule appointment with same provider on next available working day."""
    # Find next working day after unavailable period
    next_date = unavailable_end_date + timedelta(days=1)
    
    # Skip weekends
    while next_date.weekday() >= 5:  # Saturday=5, Sunday=6
        next_date += timedelta(days=1)
    
    # Try to find available slot on next working day
    # For simplicity, use same time if available
    original_time = appointment.get('time')
    new_date_str = next_date.strftime("%Y-%m-%d")
    
    # Check if slot is available (no existing appointment at that time)
    slot_available = True
    for apt in appointments:
        if (apt.get('provider_id') == provider_id and 
            apt.get('date', '').startswith(new_date_str) and 
            apt.get('time') == original_time and
            apt.get('status') == 'scheduled'):
            slot_available = False
            break
    
    if slot_available:
        # Update appointment
        appointment['date'] = f"{new_date_str}T{original_time}:00"
        appointment['status'] = 'rescheduled'
        appointment['reschedule_reason'] = 'Provider temporarily unavailable'
        appointment['rescheduled_at'] = datetime.now().isoformat()
        appointment['original_date'] = appointment.get('date')
        return True
    
    return False

def _batch_provider_matching_with_llm(appointment_patient_pairs, unavailable_provider_id, providers):
    """Batch all provider matching decisions into a single LLM call."""
    # Filter available providers
    available_providers = []
    for provider in providers:
        if (provider.get('provider_id') != unavailable_provider_id and 
            provider.get('status') == 'active'):
            available_providers.append(provider)
    
    if not available_providers or not appointment_patient_pairs:
        return {}
    
    # Create batched LLM prompt
    prompt = f"""You are a healthcare scheduling assistant. Multiple patients need to be reassigned to new providers due to their original provider being unavailable.

AVAILABLE PROVIDERS:
"""
    
    for i, provider in enumerate(available_providers, 1):
        prompt += f"""
Provider {i}: {provider.get('name', 'Unknown')} (ID: {provider.get('provider_id')})
- Specialty: {provider.get('specialty', 'Unknown')}
- Gender: {provider.get('gender', 'Unknown')}
- Experience: {provider.get('years_experience', 'Unknown')} years
- Location: {provider.get('primary_location', 'Unknown')}
- Capacity Utilization: {provider.get('capacity_utilization', 'Unknown')}
- Certifications: {', '.join(provider.get('certifications', []))}
"""
    
    prompt += "\nPATIENTS TO MATCH:\n"
    
    for i, (appointment, patient) in enumerate(appointment_patient_pairs):
        prompt += f"""
Patient {i+1}:
- Patient ID: {patient.get('patient_id', 'Unknown')}
- Condition: {patient.get('condition', 'Unknown')}
- Specialty Needed: {patient.get('condition_specialty_required', 'Physical Therapy')}
- Gender Preference: {patient.get('gender_preference', 'No preference')}
- Preferred Location: {patient.get('preferred_location', 'Any')}
- Insurance: {patient.get('insurance_provider', 'Unknown')}
- Age: {patient.get('age', 'Unknown')}
"""
    
    prompt += """
TASK:
For each patient, analyze their needs and choose the BEST provider match considering:
1. Specialty alignment with patient's condition
2. Patient's gender preference (if specified)
3. Location convenience
4. Provider experience and qualifications
5. Provider availability (lower capacity utilization is better)

Respond with ONLY a JSON object with matches for each patient:
{
    "matches": [
        {
            "patient_index": 1,
            "selected_provider_id": "P001",
            "provider_name": "Provider Name",
            "match_quality": "EXCELLENT|GOOD|FAIR",
            "reasoning": "Brief explanation of why this provider is the best match",
            "match_factors": {
                "specialty_match": true/false,
                "gender_match": true/false,
                "location_match": true/false,
                "experience_match": true/false,
                "availability_good": true/false
            }
        }
    ]
}

If no provider is suitable for a patient, use:
{
    "patient_index": X,
    "selected_provider_id": null,
    "reasoning": "No suitable provider found"
}
"""
    
    try:
        # Call LLM for batched matching
        response = _call_llm_for_matching(prompt)
        
        if response and response.get('matches'):
            # Process LLM response and create provider mapping
            provider_matches = {}
            
            for match in response['matches']:
                patient_index = match.get('patient_index', 1) - 1  # Convert to 0-based index
                selected_provider_id = match.get('selected_provider_id')
                
                if selected_provider_id and patient_index < len(appointment_patient_pairs):
                    # Find the selected provider
                    for provider in available_providers:
                        if provider.get('provider_id') == selected_provider_id:
                            matched_provider = provider.copy()
                            matched_provider['llm_match_quality'] = match.get('match_quality', 'GOOD')
                            matched_provider['llm_reasoning'] = match.get('reasoning', 'LLM selected this provider')
                            matched_provider['llm_match_factors'] = match.get('match_factors', {})
                            provider_matches[patient_index] = matched_provider
                            break
            
            return provider_matches
        
        # Fallback: if LLM fails, use simple rule-based matching for all patients
        return _fallback_batch_matching(appointment_patient_pairs, available_providers)
        
    except Exception as e:
        print(f"Batched LLM matching failed: {e}")
        # Fallback to rule-based matching
        return _fallback_batch_matching(appointment_patient_pairs, available_providers)

def _fallback_batch_matching(appointment_patient_pairs, available_providers):
    """Simple fallback matching for all patients when LLM is not available."""
    provider_matches = {}
    
    for i, (appointment, patient) in enumerate(appointment_patient_pairs):
        patient_specialty = patient.get('condition_specialty_required', '').lower()
        
        # Find provider with matching specialty
        matched_provider = None
        for provider in available_providers:
            provider_specialty = provider.get('specialty', '').lower()
            if patient_specialty in provider_specialty or provider_specialty in patient_specialty:
                matched_provider = provider.copy()
                matched_provider['llm_match_quality'] = 'GOOD'
                matched_provider['llm_reasoning'] = 'Specialty match (fallback logic)'
                matched_provider['llm_match_factors'] = {'specialty_match': True}
                break
        
        # If no specialty match, use first available provider
        if not matched_provider and available_providers:
            matched_provider = available_providers[0].copy()
            matched_provider['llm_match_quality'] = 'FAIR'
            matched_provider['llm_reasoning'] = 'First available provider (fallback logic)'
            matched_provider['llm_match_factors'] = {}
        
        if matched_provider:
            provider_matches[i] = matched_provider
    
    return provider_matches

def _find_best_matching_provider_with_llm(patient, unavailable_provider_id, providers):
    """Find best matching provider using LLM-based decision making."""
    # Filter available providers
    available_providers = []
    for provider in providers:
        if (provider.get('provider_id') != unavailable_provider_id and 
            provider.get('status') == 'active'):
            available_providers.append(provider)
    
    if not available_providers:
        return None
    
    # Create LLM prompt for provider matching
    prompt = f"""You are a healthcare scheduling assistant. A patient needs to be reassigned to a new provider due to their original provider being unavailable.

PATIENT INFORMATION:
- Patient ID: {patient.get('patient_id', 'Unknown')}
- Name: {patient.get('name', 'Unknown')}
- Condition: {patient.get('condition', 'Unknown')}
- Specialty Needed: {patient.get('condition_specialty_required', 'Physical Therapy')}
- Gender Preference: {patient.get('gender_preference', 'No preference')}
- Preferred Location: {patient.get('preferred_location', 'Any')}
- Insurance: {patient.get('insurance_provider', 'Unknown')}
- Age: {patient.get('age', 'Unknown')}

AVAILABLE PROVIDERS:
"""
    
    for i, provider in enumerate(available_providers, 1):
        prompt += f"""
Provider {i}: {provider.get('name', 'Unknown')} (ID: {provider.get('provider_id')})
- Specialty: {provider.get('specialty', 'Unknown')}
- Gender: {provider.get('gender', 'Unknown')}
- Experience: {provider.get('years_experience', 'Unknown')} years
- Location: {provider.get('primary_location', 'Unknown')}
- Capacity Utilization: {provider.get('capacity_utilization', 'Unknown')}
- Certifications: {', '.join(provider.get('certifications', []))}
"""
    
    prompt += """
TASK:
Analyze the patient's needs and available providers. Choose the BEST provider match considering:
1. Specialty alignment with patient's condition
2. Patient's gender preference (if specified)
3. Location convenience
4. Provider experience and qualifications
5. Provider availability (lower capacity utilization is better)

Respond with ONLY a JSON object in this exact format:
{
    "selected_provider_id": "P001",
    "provider_name": "Provider Name",
    "match_quality": "EXCELLENT|GOOD|FAIR",
    "reasoning": "Brief explanation of why this provider is the best match",
    "match_factors": {
        "specialty_match": true/false,
        "gender_match": true/false,
        "location_match": true/false,
        "experience_match": true/false,
        "availability_good": true/false
    }
}

If no provider is suitable, respond with:
{
    "selected_provider_id": null,
    "reasoning": "No suitable provider found"
}
"""
    
    try:
        # Try to use LLM for matching decision
        response = _call_llm_for_matching(prompt)
        
        if response and response.get('selected_provider_id'):
            # Find the selected provider
            for provider in available_providers:
                if provider.get('provider_id') == response.get('selected_provider_id'):
                    provider['llm_match_quality'] = response.get('match_quality', 'GOOD')
                    provider['llm_reasoning'] = response.get('reasoning', 'LLM selected this provider')
                    provider['llm_match_factors'] = response.get('match_factors', {})
                    return provider
        
        # Fallback: if LLM fails, use simple rule-based matching
        return _fallback_provider_matching(patient, available_providers)
        
    except Exception as e:
        print(f"LLM matching failed: {e}")
        # Fallback to rule-based matching
        return _fallback_provider_matching(patient, available_providers)

def _call_llm_for_matching(prompt):
    """Call LLM for provider matching decision with Langfuse tracing."""
    try:
        print("\n" + "="*80)
        print("🤖 LLM PROVIDER MATCHING CALL")
        print("="*80)
        print("📝 PROMPT (first 500 chars):")
        print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
        print("\n🔄 Calling LLM...")
        
        # Langfuse tracing will be handled automatically by the wrapped OpenAI client
        print("🔍 Langfuse tracing enabled via OpenAI wrapper")
        
        # Try Azure OpenAI with Langfuse tracing
        try:
            # Get Azure configuration from environment
            azure_model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-5-chat")
            azure_endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
            azure_key = os.getenv("ORCHESTRATION_LLM_AZURE_API_KEY")
            
            print(f"🔧 Azure Model: {azure_model}")
            print(f"🔧 Azure Endpoint: {azure_endpoint[:50] if azure_endpoint else 'Not set'}...")
            print(f"🔧 Azure Key: {'***' + azure_key[-4:] if azure_key else 'Not set'}")
            print(f"🔧 Condition check: endpoint={bool(azure_endpoint)}, key={bool(azure_key)}")
            
            # Configure Azure OpenAI client with Langfuse wrapper
            if azure_endpoint and azure_key:
                from langfuse.openai import AzureOpenAI
                print("✅ Using Langfuse-wrapped Azure OpenAI client")
                
                azure_client = AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=azure_key,
                    api_version="2024-02-01"
                )
                
                response = azure_client.chat.completions.create(
                    model=azure_model,
                    messages=[
                        {"role": "system", "content": "You are a healthcare scheduling assistant. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=LLMSettings.SCHEDULING_TEMPERATURE,
                    max_tokens=LLMSettings.SCHEDULING_MAX_TOKENS,
                    # Langfuse tracing metadata
                    name="provider-matching",
                    metadata={
                        "type": "batch_provider_matching", 
                        "system": "appointment_rescheduling",
                        "environment": "development",
                        "user_id": "system",
                        "session_id": f"provider_unavailable_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    }
                )
                
                print(f"🔍 Langfuse trace details:")
                print(f"   - Model: {azure_model}")
                print(f"   - Name: provider-matching")
                print(f"   - Environment: development")
                print(f"   - Endpoint: {azure_endpoint[:50]}...")
            else:
                print("⚠️  Azure credentials not found, trying direct OpenAI...")
                from langfuse.openai import openai
                response = openai.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": "You are a healthcare scheduling assistant. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=LLMSettings.SCHEDULING_TEMPERATURE,
                    max_tokens=LLMSettings.SCHEDULING_MAX_TOKENS,
                    name="provider-matching",
                    metadata={"type": "batch_provider_matching", "system": "appointment_rescheduling"}
                )
            
            if response and response.choices and response.choices[0].message.content:
                content = response.choices[0].message.content
                print("✅ LLM Response received (first 300 chars):")
                print(content[:300] + "..." if len(content) > 300 else content)
                
                import json
                result = json.loads(content.strip())
                print("📊 Parsed LLM Result:")
                print(f"   Matches found: {len(result.get('matches', []))}")
                for i, match in enumerate(result.get('matches', [])[:3]):  # Show first 3
                    print(f"   Match {i+1}: {match.get('selected_provider_id')} - {match.get('match_quality')}")
                print("="*80 + "\n")
                
                # Trace will be automatically completed by Langfuse OpenAI wrapper
                print("✅ LLM call completed - trace sent to Langfuse")
                
                # Ensure traces are flushed to Langfuse
                if langfuse:
                    try:
                        langfuse.flush()
                        print("🚀 Langfuse traces flushed")
                    except Exception as flush_e:
                        print(f"⚠️  Langfuse flush failed: {flush_e}")
                
                return result
                
        except ImportError:
            print("⚠️  Langfuse not available, trying LiteLLMAdapter...")
            
            # Fallback to LiteLLMAdapter (if available)
            try:
                from adapters.llm.litellm_adapter import LiteLLMAdapter
                print("✅ Using LiteLLMAdapter with Langfuse tracing")
                
                llm = LiteLLMAdapter(
                    model=LLMSettings.ORCHESTRATOR_MODEL,
                    api_base=LLMSettings.LITELLM_BASE_URL,
                    api_key=LLMSettings.LITELLM_API_KEY,
                    enable_langfuse=True
                )
                
                response = llm.generate(
                    prompt=prompt,
                    system="You are a healthcare scheduling assistant. Respond only with valid JSON.",
                    max_tokens=LLMSettings.SCHEDULING_MAX_TOKENS,
                    temperature=LLMSettings.SCHEDULING_TEMPERATURE,
                    metadata={"type": "batch_provider_matching", "system": "appointment_rescheduling", "trace_name": "provider-matching"}
                )
                
                if response and response.content:
                    print("✅ LLM Response received (first 300 chars):")
                    print(response.content[:300] + "..." if len(response.content) > 300 else response.content)
                    
                    import json
                    result = json.loads(response.content.strip())
                    print("📊 Parsed LLM Result:")
                    print(f"   Matches found: {len(result.get('matches', []))}")
                    for i, match in enumerate(result.get('matches', [])[:3]):  # Show first 3
                        print(f"   Match {i+1}: {match.get('selected_provider_id')} - {match.get('match_quality')}")
                    print("="*80 + "\n")
                    
                    # Update trace with result
                    if trace:
                        try:
                            trace.update(
                                output={"matches_count": len(result.get('matches', [])), "status": "success"},
                                status_message="LLM matching completed successfully"
                            )
                        except Exception as e:
                            print(f"⚠️  Trace update failed: {e}")
                    
                    return result
                    
            except ImportError:
                print("⚠️  LiteLLMAdapter not available, trying direct Langfuse...")
            
            # Fallback to direct Langfuse OpenAI wrapper
            try:
                from langfuse.openai import openai
                print("✅ Using direct Langfuse-wrapped OpenAI client")
                
                response = openai.chat.completions.create(
                    model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                    messages=[
                        {"role": "system", "content": "You are a healthcare scheduling assistant. Respond only with valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=LLMSettings.SCHEDULING_TEMPERATURE,
                    max_tokens=LLMSettings.SCHEDULING_MAX_TOKENS,
                    name="provider-matching",
                    metadata={"type": "batch_provider_matching", "system": "appointment_rescheduling"}
                )
                
                if response and response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content
                    print("✅ LLM Response received (direct Langfuse)")
                    import json
                    result = json.loads(content.strip())
                    print("📊 Parsed LLM Result:")
                    print(f"   Matches found: {len(result.get('matches', []))}")
                    print("="*80 + "\n")
                    return result
                    
            except ImportError:
                print("⚠️  Langfuse not available either, trying basic LiteLLM...")
                
                # Final fallback to basic LiteLLM
                from litellm import completion
                
                # Use Azure configuration for LiteLLM fallback
                azure_model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-5-chat")
                azure_endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
                azure_key = os.getenv("ORCHESTRATION_LLM_AZURE_API_KEY")
                
                if azure_endpoint and azure_key:
                    response = completion(
                        model=f"azure/{azure_model}",
                        messages=[
                            {"role": "system", "content": "You are a healthcare scheduling assistant. Respond only with valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=LLMSettings.SCHEDULING_TEMPERATURE,
                        max_tokens=LLMSettings.SCHEDULING_MAX_TOKENS,
                        api_base=azure_endpoint,
                        api_key=azure_key,
                        api_version="2024-02-01"
                    )
                else:
                    response = completion(
                        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                        messages=[
                            {"role": "system", "content": "You are a healthcare scheduling assistant. Respond only with valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=LLMSettings.SCHEDULING_TEMPERATURE,
                        max_tokens=LLMSettings.SCHEDULING_MAX_TOKENS
                    )
                
                if response and response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content
                    print("✅ LLM Response received (basic LiteLLM)")
                    import json
                    result = json.loads(content.strip())
                    print("📊 Parsed LLM Result:")
                    print(f"   Matches found: {len(result.get('matches', []))}")
                    print("="*80 + "\n")
                    return result
            
    except ImportError:
        print("❌ No LLM adapters available, using fallback matching")
        print("="*80 + "\n")
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        print("   Falling back to rule-based matching...")
        print("="*80 + "\n")
        
        # Error will be automatically traced by Langfuse OpenAI wrapper
        print(f"⚠️  LLM call failed - error traced to Langfuse: {str(e)}")
    
    return None

def _fallback_provider_matching(patient, available_providers):
    """Simple fallback matching when LLM is not available."""
    # Simple rule: find provider with matching specialty
    patient_specialty = patient.get('condition_specialty_required', '').lower()
    
    for provider in available_providers:
        provider_specialty = provider.get('specialty', '').lower()
        if patient_specialty in provider_specialty or provider_specialty in patient_specialty:
            provider['llm_match_quality'] = 'GOOD'
            provider['llm_reasoning'] = 'Specialty match (fallback logic)'
            provider['llm_match_factors'] = {'specialty_match': True}
            return provider
    
    # If no specialty match, return first available provider
    if available_providers:
        provider = available_providers[0]
        provider['llm_match_quality'] = 'FAIR'
        provider['llm_reasoning'] = 'First available provider (fallback logic)'
        provider['llm_match_factors'] = {}
        return provider
    
    return None

def _reschedule_different_provider(appointment, new_provider_id, appointments):
    """Try to reschedule appointment with different provider at same time."""
    original_date = appointment.get('date', '').split('T')[0]
    original_time = appointment.get('time')
    
    # Check if new provider is available at same time
    slot_available = True
    for apt in appointments:
        if (apt.get('provider_id') == new_provider_id and 
            apt.get('date', '').startswith(original_date) and 
            apt.get('time') == original_time and
            apt.get('status') == 'scheduled'):
            slot_available = False
            break
    
    if slot_available:
        # Update appointment
        appointment['provider_id'] = new_provider_id
        appointment['status'] = 'rescheduled'
        appointment['reschedule_reason'] = 'Provider reassignment due to unavailability'
        appointment['rescheduled_at'] = datetime.now().isoformat()
        appointment['original_provider_id'] = appointment.get('provider_id')
        appointment['reassigned'] = True
        return True
    
    return False

def _generate_ai_personalized_email(appointment, patient, old_provider, new_provider, reason):
    """Generate AI-personalized email content."""
    try:
        from langfuse.openai import openai
        
        appointment_date = appointment.get('date', '').split('T')[0]
        appointment_time = appointment.get('time', '')
        
        prompt = f"""Write a personalized, empathetic email to reschedule a patient's appointment.

Patient Details:
- Name: {patient.get('name')}
- Condition: {patient.get('condition')}
- Original appointment: {appointment_date} at {appointment_time}

Situation:
- Original provider: {old_provider.get('name')} ({old_provider.get('specialty', 'Healthcare Provider')})
- Reason for change: {reason}
- New provider: {new_provider.get('name')} ({new_provider.get('specialty', 'Healthcare Provider')})
- Location: {new_provider.get('primary_location', 'Metro PT Downtown')}

Requirements:
- Be empathetic and professional
- Explain the situation clearly
- Highlight the new provider's qualifications
- Keep it concise but warm
- End with clinic contact: Metro Physical Therapy, (555) 123-4567
- Use minimal formatting - avoid excessive bold text or markdown
- Write in a natural, conversational tone
- DO NOT include any confirmation links or buttons in the email body
- DO NOT ask the patient to "click here" or "confirm" - the UI will handle confirmation

Write only the email body (no subject line)."""

        # Get Azure configuration
        azure_model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-5-chat")
        azure_endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
        azure_key = os.getenv("ORCHESTRATION_LLM_AZURE_API_KEY")
        
        if azure_endpoint and azure_key:
            print(f"✅ Using Azure {azure_model} for personalized email")
            # Create Langfuse-wrapped Azure OpenAI client
            from langfuse.openai import AzureOpenAI
            azure_client = AzureOpenAI(
                azure_endpoint=azure_endpoint,
                api_key=azure_key,
                api_version="2024-02-01"
            )
            
            response = azure_client.chat.completions.create(
                model=azure_model,
                messages=[
                    {"role": "system", "content": "You are a compassionate healthcare communication specialist. Write warm, professional emails that put patients at ease."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                # Langfuse tracing metadata
                name="personalized-email",
                metadata={
                    "type": "personalized_email", 
                    "patient": patient.get('name'),
                    "environment": "development",
                    "user_id": "system",
                    "session_id": f"email_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                }
            )
            
            print(f"📧 Email generation trace:")
            print(f"   - Patient: {patient.get('name')}")
            print(f"   - Model: {azure_model}")
            print(f"   - Name: personalized-email")
        else:
            print("⚠️  Using fallback OpenAI model for personalized email")
            from langfuse.openai import openai
            response = openai.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a compassionate healthcare communication specialist. Write warm, professional emails that put patients at ease."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                name="personalized-email",
                metadata={"type": "personalized_email", "patient": patient.get('name')}
            )
        
        if response and response.choices and response.choices[0].message.content:
            # Ensure email generation traces are flushed to Langfuse
            if 'langfuse' in globals() and langfuse:
                try:
                    langfuse.flush()
                    print("📧 Email generation trace flushed to Langfuse")
                except Exception as flush_e:
                    print(f"⚠️  Email trace flush failed: {flush_e}")
            
            # Process the AI-generated email
            email_content = response.choices[0].message.content.strip()
            
            # Clean up excessive markdown formatting
            import re
            # Reduce multiple consecutive ** to single **
            email_content = re.sub(r'\*\*+', '**', email_content)
            # Limit bold formatting to key terms only
            email_content = re.sub(r'\*\*(.*?)\*\*', lambda m: f"**{m.group(1)}**" if len(m.group(1)) < 30 else m.group(1), email_content)
            
            # Remove any confirmation links that might have been generated despite instructions
            email_content = re.sub(r'[Pp]lease confirm.*?(?:clicking|link).*?[./]', '', email_content)
            email_content = re.sub(r'[Cc]lick here.*?[./]', '', email_content)
            email_content = re.sub(r'\[.*?[Cc]onfirm.*?\]\(.*?\)', '', email_content)  # Remove markdown links
            email_content = re.sub(r'http[s]?://[^\s]+', '', email_content)  # Remove any URLs
            
            # Clean up extra whitespace and line breaks
            email_content = re.sub(r'\n\s*\n\s*\n', '\n\n', email_content)  # Remove triple+ line breaks
            email_content = email_content.strip()
            
            return email_content
            
    except Exception as e:
        print(f"AI email generation failed: {e}")
    
    return None

def _send_rescheduling_email(appointment, patient, old_provider, new_provider, reason):
    """Send rescheduling notification email to patient."""
    try:
        # Format date and time
        appointment_date = appointment.get('date', '').split('T')[0]
        appointment_time = appointment.get('time', '')
        
        # Try to generate AI-personalized email first
        ai_email_body = _generate_ai_personalized_email(appointment, patient, old_provider, new_provider, reason)
        
        if ai_email_body:
            # Use AI-generated content
            email_data = {
                'to': patient.get('email', 'patient@example.com'),
                'subject': f"Important: Your Appointment on {appointment_date} at {appointment_time}",
                'body': ai_email_body,
                'template': 'ai_personalized'
            }
            print("✅ Using AI-generated personalized email")
        else:
            # Fallback to template
            email_data = EmailTemplates.render_offer(
                patient_name=patient.get('name', 'Patient'),
                patient_email=patient.get('email', 'patient@example.com'),
                date=appointment_date,
                time=appointment_time,
                reason=reason,
                original_provider=old_provider.get('name', 'Previous Provider'),
                new_provider=new_provider.get('name', 'New Provider'),
                specialty=new_provider.get('specialty', 'Healthcare'),
                location=new_provider.get('primary_location', 'Clinic'),
                condition=patient.get('condition', 'your condition'),
                confirmation_link=f"/confirm?token={appointment.get('appointment_id')}",
                clinic_name="Metro Physical Therapy",
                clinic_phone="(555) 123-4567"
            )
            print("⚠️  Using template fallback email")
        
        # Send email using mock system
        result = mock_send_email(
            to=email_data['to'],
            subject=email_data['subject'],
            body=email_data['body'],
            template=email_data['template']
        )
        
        # Also save to emails.json for the API endpoint
        try:
            emails_file = DATA_DIR / "emails.json"
            if emails_file.exists():
                with open(emails_file, 'r') as f:
                    emails = json.load(f)
            else:
                emails = []
            
            # Add email record
            email_record = {
                "email_id": result.get('email_id', f"EMAIL-{len(emails) + 1:03d}"),
                "to": email_data['to'],
                "subject": email_data['subject'],
                "body": email_data['body'],
                "template": email_data['template'],
                "appointment_id": appointment.get('appointment_id'),
                "patient_name": patient.get('name'),
                "provider_name": new_provider.get('name'),
                "date": appointment_date,
                "time": appointment_time,
                "sent_at": datetime.now().isoformat(),
                "status": "pending",  # Changed from "sent" to "pending" for confirmation
                # Add confirmation URLs (dynamic, not hardcoded)
                "confirm_url": f"/confirm?token={appointment.get('appointment_id')}&action=accept",
                "decline_url": f"/confirm?token={appointment.get('appointment_id')}&action=decline"
            }
            emails.append(email_record)
            
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2)
                
        except Exception as e:
            print(f"Error saving email to JSON: {e}")
        
        return result.get('email_id') is not None
        
    except Exception as e:
        print(f"Error sending rescheduling email: {e}")
        return False

def _add_to_waitlist(appointment, patient, reason):
    """Add patient to waitlist when no suitable rescheduling option is available."""
    try:
        waitlist_file = DATA_DIR / "waitlist.json"
        
        # Load existing waitlist
        if waitlist_file.exists():
            with open(waitlist_file, 'r') as f:
                waitlist = json.load(f)
        else:
            waitlist = []
        
        # Create waitlist entry
        waitlist_entry = {
            "waitlist_id": f"WL{len(waitlist) + 1:03d}",
            "patient_id": appointment.get('patient_id'),
            "name": patient.get('name', 'Unknown'),
            "condition": patient.get('condition', 'Unknown'),
            "no_show_risk": patient.get('no_show_risk', 0.5),
            "priority": "HIGH",  # High priority due to provider unavailability
            "requested_specialty": patient.get('condition_specialty_required', 'Physical Therapy'),
            "requested_location": patient.get('preferred_location', 'Any'),
            "availability_windows": {
                "days": patient.get('preferred_days', 'Monday,Tuesday,Wednesday,Thursday,Friday').split(','),
                "times": ["Morning", "Afternoon"]
            },
            "insurance": patient.get('insurance_provider', 'Unknown'),
            "current_appointment": appointment.get('appointment_id'),
            "willing_to_move_up": True,
            "added_to_waitlist": datetime.now().isoformat() + "Z",
            "waitlist_reason": reason,
            "notes": f"Original appointment {appointment.get('appointment_id')} affected by provider unavailability"
        }
        
        waitlist.append(waitlist_entry)
        
        # Save updated waitlist
        with open(waitlist_file, 'w') as f:
            json.dump(waitlist, f, indent=2)
        
        # Update original appointment status - cancel the conflicting appointment
        appointment['status'] = 'cancelled'
        appointment['cancellation_reason'] = f'Provider unavailable - added to waitlist: {reason}'
        appointment['cancelled_at'] = datetime.now().isoformat()
        appointment['waitlist_reason'] = reason
        appointment['waitlisted_at'] = datetime.now().isoformat()
        
    except Exception as e:
        print(f"Error adding to waitlist: {e}")
        # Fallback: just cancel the appointment
        appointment['status'] = 'cancelled'
        appointment['cancellation_reason'] = f'Provider unavailable - waitlist error: {str(e)}'

@app.post("/api/demo/reset")
async def reset_demo_data(request: DemoResetRequest):
    """Reset demo data with realistic appointments - ADMIN ONLY."""
    # Admin protection
    if request.admin_key != "demo_admin_2024":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Valid admin_key required in request body."
        )
    
    try:
        # File paths
        appointments_file = DATA_DIR / "appointments.json"
        providers_file = DATA_DIR / "providers.json"
        patients_file = DATA_DIR / "patients.json"
        emails_file = DATA_DIR / "emails.json"
        waitlist_file = DATA_DIR / "waitlist.json"
        freed_slots_file = DATA_DIR / "freed_slots.json"
        seed_file = DATA_DIR / "demo_seed_appointments.json"
        
        # Load existing data
        with open(providers_file, 'r') as f:
            providers = json.load(f)
        
        # Load realistic patient data
        if seed_file.exists():
            with open(seed_file, 'r') as f:
                seed_data = json.load(f)
                realistic_patients = seed_data.get('realistic_appointments', [])
        else:
            # Fallback realistic patients
            realistic_patients = [
                {"patient_id": "PAT001", "patient_name": "Maria Rodriguez", "condition": "knee pain", "specialty_needed": "Orthopedic Physical Therapy"},
                {"patient_id": "PAT002", "patient_name": "John Smith", "condition": "sports injury", "specialty_needed": "Sports Physical Therapy"},
                {"patient_id": "PAT003", "patient_name": "Sarah Johnson", "condition": "back pain", "specialty_needed": "General Physical Therapy"}
            ]
        
        # Generate appointments
        appointments = []
        appointment_counter = 1
        start_date = datetime.now().date()
        current_time = datetime.now()
        time_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
        
        # Provider specialty mapping
        provider_specialty_map = {p['provider_id']: p.get('specialty', '') for p in providers}
        
        # Track used patients globally to avoid duplicates across days
        used_patients = set()
        available_patients = [p for p in realistic_patients if p.get('match_type') != 'waitlist']
        
        for day_offset in range(request.days_ahead):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Track used slots per provider to avoid overlaps
            provider_slots_used = {p['provider_id']: set() for p in providers}
            appointments_for_day = 0
            
            # Get patients for this day - prioritize unique patients first
            day_patients = []
            
            # First, try to get unique patients (not used on any previous day)
            for patient_data in available_patients:
                if patient_data['patient_id'] not in used_patients and len(day_patients) < request.appointments_per_day:
                    day_patients.append(patient_data)
                    used_patients.add(patient_data['patient_id'])
            
            # If we need more patients, reuse from the beginning (but still avoid same-day duplicates)
            if len(day_patients) < request.appointments_per_day:
                remaining_needed = request.appointments_per_day - len(day_patients)
                patient_cycle_index = 0
                while len(day_patients) < request.appointments_per_day and patient_cycle_index < len(available_patients):
                    patient_data = available_patients[patient_cycle_index]
                    # Avoid duplicates within the same day
                    if not any(p['patient_id'] == patient_data['patient_id'] for p in day_patients):
                        day_patients.append(patient_data)
                    patient_cycle_index += 1
            
            for patient_data in day_patients:
                
                # Match patient to appropriate provider
                matched_provider = None
                for provider in providers:
                    if provider_specialty_map.get(provider['provider_id']) == patient_data.get('specialty_needed'):
                        matched_provider = provider
                        break
                
                if not matched_provider and providers:
                    matched_provider = providers[0]
                
                if matched_provider:
                    # Find available time slot
                    available_slot = None
                    for time_slot in time_slots:
                        # Skip past times if it's today
                        if current_date == current_time.date():
                            slot_time = datetime.strptime(time_slot, "%H:%M").time()
                            if slot_time <= current_time.time():
                                continue
                        
                        if time_slot not in provider_slots_used[matched_provider['provider_id']]:
                            available_slot = time_slot
                            provider_slots_used[matched_provider['provider_id']].add(time_slot)
                            break
                    
                    if available_slot:
                        appointment = {
                            "appointment_id": f"A{appointment_counter:03d}",
                            "patient_id": patient_data['patient_id'],
                            "provider_id": matched_provider['provider_id'],
                            "date": current_date.strftime("%Y-%m-%dT") + available_slot + ":00",
                            "time": available_slot,
                            "status": "scheduled",
                            "confirmation_number": f"CONF-{appointment_counter:03d}",
                            "reassigned": False,
                            "confirmation_status": "confirmed"
                        }
                        appointments.append(appointment)
                        appointment_counter += 1
                        appointments_for_day += 1
                        # Continue to next patient (don't break the patient loop)
        
        # Save all data
        with open(appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        with open(emails_file, 'w') as f:
            json.dump([], f, indent=2)
        
        with open(waitlist_file, 'w') as f:
            json.dump([], f, indent=2)
        
        with open(freed_slots_file, 'w') as f:
            json.dump([], f, indent=2)
        
        # Reset provider status
        for provider in providers:
            provider['unavailable_dates'] = []
            provider['status'] = 'active'
        with open(providers_file, 'w') as f:
            json.dump(providers, f, indent=2)
        
        return {
            "success": True,
            "message": "Demo data reset successfully",
            "appointments_created": len(appointments),
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": (start_date + timedelta(days=request.days_ahead - 1)).strftime("%Y-%m-%d")
            },
            "providers_included": len(providers),
            "patients_used": len(realistic_patients),
            "appointments_per_day": request.appointments_per_day
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resetting demo data: {str(e)}")

# ============================================================
# HTML Pages
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Comprehensive index page with all available URLs and endpoints."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WebTP Demo - Index</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 1200px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2.5rem;
                text-align: center;
            }
            .subtitle {
                color: #7f8c8d;
                margin-bottom: 40px;
                font-size: 1.1rem;
                text-align: center;
            }
            .section {
                margin-bottom: 40px;
            }
            .section-title {
                color: #2c3e50;
                font-size: 1.5rem;
                margin-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 10px;
            }
            .url-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }
            .url-card {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 20px;
                text-decoration: none;
                color: #2c3e50;
                transition: all 0.3s;
                display: block;
            }
            .url-card:hover {
                transform: translateY(-3px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                border-color: #667eea;
            }
            .url-header {
                display: flex;
                align-items: center;
                margin-bottom: 10px;
            }
            .url-icon {
                font-size: 1.5rem;
                margin-right: 10px;
            }
            .url-title {
                font-weight: 600;
                font-size: 1.1rem;
            }
            .url-path {
                font-family: 'Monaco', 'Menlo', monospace;
                background: #e9ecef;
                padding: 5px 8px;
                border-radius: 4px;
                font-size: 0.9rem;
                margin-bottom: 8px;
                color: #495057;
            }
            .url-desc {
                color: #6c757d;
                font-size: 0.9rem;
                line-height: 1.4;
            }
            .api-section {
                background: #f1f3f4;
                border-radius: 8px;
                padding: 20px;
                margin-top: 20px;
            }
            .method-badge {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-right: 8px;
            }
            .get { background: #d4edda; color: #155724; }
            .post { background: #d1ecf1; color: #0c5460; }
            .put { background: #fff3cd; color: #856404; }
            .delete { background: #f8d7da; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 WebTP Demo Index</h1>
            <p class="subtitle">Complete directory of all available pages and endpoints</p>
            
            <!-- Main UI Pages -->
            <div class="section">
                <h2 class="section-title">🖥️ User Interface Pages</h2>
                <div class="url-grid">
                    <a href="/schedule.html" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📅</span>
                            <span class="url-title">Appointment Schedule</span>
                        </div>
                        <div class="url-path">/schedule.html</div>
                        <div class="url-desc">Interactive calendar showing all appointments, provider availability, and real-time scheduling</div>
                    </a>
                    
                    <a href="/emails.html" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📧</span>
                            <span class="url-title">Patient Emails</span>
                        </div>
                        <div class="url-path">/emails.html</div>
                        <div class="url-desc">View AI-generated patient communications, confirmations, and rescheduling notifications</div>
                    </a>
                    
                </div>
            </div>
            
            <!-- API Documentation -->
            <div class="section">
                <h2 class="section-title">📚 API Documentation</h2>
                <div class="url-grid">
                    <a href="/docs" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📖</span>
                            <span class="url-title">Interactive API Docs</span>
                        </div>
                        <div class="url-path">/docs</div>
                        <div class="url-desc">Swagger UI with interactive API testing, request/response examples, and endpoint documentation</div>
                    </a>
                    
                    <a href="/redoc" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📋</span>
                            <span class="url-title">ReDoc Documentation</span>
                        </div>
                        <div class="url-path">/redoc</div>
                        <div class="url-desc">Clean, readable API documentation with detailed schemas and examples</div>
                    </a>
                    
                    <a href="/openapi.json" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">⚙️</span>
                            <span class="url-title">OpenAPI Schema</span>
                        </div>
                        <div class="url-path">/openapi.json</div>
                        <div class="url-desc">Raw OpenAPI 3.0 specification for API integration and client generation</div>
                    </a>
                </div>
            </div>
            
            <!-- Key API Endpoints -->
            <div class="section">
                <h2 class="section-title">🔌 Key API Endpoints</h2>
                <div class="api-section">
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge get">GET</span>
                        <code>/health</code> - Health check endpoint
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge get">GET</span>
                        <code>/api/appointments</code> - Get all appointments
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge get">GET</span>
                        <code>/api/providers</code> - Get all providers
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge get">GET</span>
                        <code>/api/patients</code> - Get all patients
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge post">POST</span>
                        <code>/api/demo/reset</code> - Reset demo data with realistic appointments
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge post">POST</span>
                        <code>/api/providers/{provider_id}/unavailable</code> - Mark provider unavailable
                    </div>
                    <div style="margin-bottom: 15px;">
                        <span class="method-badge post">POST</span>
                        <code>/api/patient-response</code> - Handle patient email responses
                    </div>
                    <div>
                        <span class="method-badge get">GET</span>
                        <code>/api/emails</code> - Get sent emails
                    </div>
                </div>
            </div>
            
            <!-- System Status -->
            <div class="section">
                <h2 class="section-title">🔍 System Status</h2>
                <div class="url-grid">
                    <a href="/health" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">💚</span>
                            <span class="url-title">Health Check</span>
                        </div>
                        <div class="url-path">/health</div>
                        <div class="url-desc">System health status and uptime information</div>
                    </a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ecf0f1; color: #7f8c8d;">
                <p>🚀 WebTP Demo - Physical Therapy Scheduling & AI Assistant</p>
                <p style="font-size: 0.9rem; margin-top: 5px;">All endpoints are live and ready for testing</p>
            </div>
        </div>
    </body>
    </html>
    """)

@app.get("/schedule.html", response_class=FileResponse)
async def get_schedule():
    """Serve schedule HTML page."""
    file_path = static_dir / "schedule.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Schedule page not found")
    return FileResponse(str(file_path), media_type="text/html")

@app.get("/emails.html", response_class=FileResponse)
async def get_emails():
    """Serve emails HTML page."""
    file_path = static_dir / "emails.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Emails page not found")
    return FileResponse(str(file_path), media_type="text/html")

@app.get("/admin/reset.html", response_class=FileResponse)
async def get_reset(admin_key: str = None):
    """Serve reset HTML page - ADMIN ONLY."""
    # Simple admin protection - in production, use proper authentication
    if admin_key != "demo_admin_2024":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin key required. Use: /admin/reset.html?admin_key=demo_admin_2024"
        )
    
    file_path = static_dir / "reset.html"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Reset page not found")
    return FileResponse(str(file_path), media_type="text/html")

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "WebTP Demo UI is running"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🌐 Starting WebTP Demo UI on port {port}")
    print(f"📱 Access at: http://localhost:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
