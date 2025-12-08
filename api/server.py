"""FastAPI Server with Swagger Documentation.

Provides REST API endpoints for the Healthcare Operations Assistant.
Includes automatic Swagger UI at /docs and ReDoc at /redoc.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.json_client import JSONClient

# Define paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Initialize FastAPI app
app = FastAPI(
    title="Healthcare Operations Assistant API",
    description="""
    REST API for the Healthcare Operations Assistant.
    
    ## Features
    - Patient management
    - Provider management
    - Appointment scheduling
    - Patient response simulation
    
    ## Try it out
    Use the interactive documentation below to test endpoints!
    """,
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize JSON client
json_client = JSONClient()

# ============================================================
# Pydantic Models for Request/Response
# ============================================================

class HealthResponse(BaseModel):
    status: str
    message: str

class Patient(BaseModel):
    patient_id: str
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    zip: Optional[str] = None
    condition: Optional[str] = None
    condition_specialty_required: Optional[str] = None
    gender_preference: Optional[str] = None
    preferred_days: Optional[str] = None
    preferred_time_block: Optional[str] = None
    max_distance_miles: Optional[float] = None
    insurance_provider: Optional[str] = None
    preferred_location: Optional[str] = None
    communication_channel_primary: Optional[str] = "email"
    no_show_risk: Optional[float] = 0.0
    prior_providers: Optional[List[str]] = []

class TimeSlot(BaseModel):
    date: str
    time: str
    available: bool

class Provider(BaseModel):
    provider_id: str
    name: str
    specialty: str
    specialties: Optional[List[str]] = []  # Multiple specialties
    primary_location: Optional[str] = None
    zip: Optional[str] = None
    gender: Optional[str] = None
    years_experience: Optional[int] = None  # Years of professional experience
    experience_level: Optional[str] = None  # junior, mid-level, senior
    certifications: Optional[List[str]] = []
    available_days: Optional[List[str]] = []  # Days of week provider normally works
    unavailable_dates: Optional[List[str]] = []  # Specific dates provider is unavailable (YYYY-MM-DD)
    working_hours_start: Optional[str] = "08:00"  # Daily start time
    working_hours_end: Optional[str] = "17:00"  # Daily end time
    available_slots: Optional[List[TimeSlot]] = []  # Available time slots
    max_patient_capacity: Optional[int] = 50
    current_patient_load: Optional[int] = 0
    distance_from_maria: Optional[float] = None
    capacity_utilization: Optional[float] = None
    status: Optional[str] = "active"  # active, on_leave, unavailable

class Appointment(BaseModel):
    model_config = {"extra": "allow"}  # Allow extra fields from JSON
    
    appointment_id: str
    patient_id: str
    provider_id: str
    date: str
    time: str
    status: Optional[str] = "scheduled"  # scheduled, completed, cancelled, pending_review, needs_attention, pending_confirmation, confirmed
    confirmation_number: Optional[str] = None
    confirmation_status: Optional[str] = None  # pending, confirmed, declined
    reassigned: Optional[bool] = False  # True if this was reassigned from another provider
    original_provider_id: Optional[str] = None  # Track original provider if reassigned
    needs_manual_review: Optional[bool] = False
    requires_review: Optional[bool] = False
    review_reason: Optional[str] = None
    match_score: Optional[int] = None  # AI match score (0-165 points)
    match_factors: Optional[Dict[str, Any]] = None  # Detailed scoring breakdown

class PatientResponseRequest(BaseModel):
    token: str
    response: str  # "yes", "no", "info"

class AppointmentUpdateRequest(BaseModel):
    provider_id: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    status: Optional[str] = None
    reassignment_reason: Optional[str] = None

class AppointmentReassignRequest(BaseModel):
    new_provider_id: str
    reason: Optional[str] = "Provider reassignment"

class ProviderUnavailableRequest(BaseModel):
    provider_id: str
    reason: str  # sick, vacation, emergency, left_organization
    start_date: str  # YYYY-MM-DD
    end_date: Optional[str] = None  # YYYY-MM-DD, defaults to start_date
    permanent: bool = False  # True if provider has left organization

class WaitlistEntry(BaseModel):
    waitlist_id: Optional[str] = None
    patient_id: str
    name: str
    condition: str
    no_show_risk: float
    priority: str  # HIGH, MEDIUM, LOW
    requested_specialty: str
    requested_location: Optional[str] = "Any"
    availability_windows: Optional[Dict[str, List[str]]] = None
    insurance: Optional[str] = None
    current_appointment: Optional[Dict[str, Any]] = None
    willing_to_move_up: bool = True
    notes: Optional[str] = None

class FreedSlot(BaseModel):
    slot_id: Optional[str] = None
    provider_id: str
    date: str
    time: str
    duration_minutes: int = 60
    specialty: str
    location: str
    reason_freed: str
    status: Optional[str] = "available"

# ============================================================
# Health Check
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health Check",
    description="Check if the API server is running"
)
async def health_check():
    """Check API health status."""
    return HealthResponse(
        status="healthy",
        message="Healthcare Operations Assistant API is running"
    )

@app.get(
    "/",
    response_class=HTMLResponse,
    tags=["System"],
    summary="API Info",
    description="Get API information and links to documentation"
)
async def root():
    """Root endpoint with API information."""
    return """
    <html>
        <head>
            <title>Healthcare Operations Assistant API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
                h1 { color: #2c3e50; }
                .endpoint { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
                .method { font-weight: bold; color: #27ae60; }
                a { color: #3498db; text-decoration: none; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>🏥 Healthcare Operations Assistant API</h1>
            <p>REST API for managing patients, providers, and appointments.</p>
            
            <h2>📚 Documentation</h2>
            <ul>
                <li><a href="/docs">Swagger UI (Interactive)</a> - Test endpoints here!</li>
                <li><a href="/redoc">ReDoc (Beautiful docs)</a></li>
                <li><a href="/openapi.json">OpenAPI Schema (JSON)</a></li>
            </ul>
            
            <h2>🔗 Quick Links</h2>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/api/appointments">/api/appointments</a> - List all appointments
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/api/providers">/api/providers</a> - List all providers
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/api/patients">/api/patients</a> - List all patients
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/health">/health</a> - Health check
            </div>
            
            <h2>📧 UI Pages</h2>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/emails.html" target="_blank">/emails.html</a> - Email inbox (standalone HTML)
            </div>
            <div class="endpoint">
                <span class="method">GET</span> <a href="/schedule.html" target="_blank">/schedule.html</a> - Appointment schedule (coming soon)
            </div>
        </body>
    </html>
    """


@app.get(
    "/emails.html",
    response_class=FileResponse,
    tags=["UI"],
    summary="Email Inbox Page",
    description="Standalone HTML page showing sent emails"
)
async def get_emails_page():
    """Serve standalone email inbox page."""
    static_dir = Path(__file__).parent.parent / "static"
    emails_file = static_dir / "emails.html"
    
    if not emails_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Email page not found at {emails_file}"
        )
    
    return FileResponse(
        str(emails_file),
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )


@app.get(
    "/schedule.html",
    response_class=FileResponse,
    tags=["UI"],
    summary="Appointment Schedule Page",
    description="Standalone HTML page showing appointment calendar"
)
async def get_schedule_page():
    """Serve standalone calendar page."""
    static_dir = Path(__file__).parent.parent / "static"
    schedule_file = static_dir / "schedule.html"
    
    if not schedule_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Schedule page not found. Create static/schedule.html first."
        )
    
    return FileResponse(
        str(schedule_file),
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )

@app.get(
    "/reset.html",
    response_class=FileResponse,
    tags=["UI"],
    summary="Demo Reset Control Page",
    description="Simple UI to reset demo data"
)
async def get_reset_page():
    """Serve demo reset control page."""
    static_dir = Path(__file__).parent.parent / "static"
    reset_file = static_dir / "reset.html"
    
    if not reset_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Reset page not found."
        )
    
    return FileResponse(
        str(reset_file),
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )

# ============================================================
# Appointments
# ============================================================

@app.get("/api/test-raw-appointments")
async def test_raw_appointments():
    """DEBUG: Return raw appointment file to test if match_score is present"""
    import json
    from pathlib import Path
    file_path = Path(__file__).parent.parent / "data" / "appointments.json"
    with open(file_path, 'r') as f:
        return json.load(f)

@app.get(
    "/api/appointments",
    # Removed response_model to return raw JSON with all fields including match_score
    tags=["Appointments"],
    summary="List Appointments",
    description="Get all appointments, optionally filtered by provider"
)
async def get_appointments(
    provider_id: Optional[str] = Query(None, description="Filter by provider ID (e.g., T001)")
):
    """
    Get appointments with optional filtering.
    
    - **provider_id**: Optional provider ID to filter appointments
    """
    try:
        appointments = json_client._load_json(json_client.appointments_file)
        
        if provider_id:
            appointments = [a for a in appointments if a.get("provider_id") == provider_id]
        
        return appointments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/appointments/{appointment_id}",
    response_model=Appointment,
    tags=["Appointments"],
    summary="Get Appointment",
    description="Get a specific appointment by ID"
)
async def get_appointment(appointment_id: str):
    """Get a single appointment by ID."""
    try:
        appointment = json_client.get_appointment(appointment_id)
        
        if not appointment:
            raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
        
        return appointment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Providers
# ============================================================

@app.get(
    "/api/providers",
    response_model=List[Provider],
    tags=["Providers"],
    summary="List Providers",
    description="Get all healthcare providers"
)
async def get_providers():
    """Get all providers."""
    try:
        return json_client._load_json(json_client.providers_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/providers/{provider_id}",
    response_model=Provider,
    tags=["Providers"],
    summary="Get Provider",
    description="Get a specific provider by ID"
)
async def get_provider(provider_id: str):
    """Get a single provider by ID."""
    try:
        provider = json_client.get_provider(provider_id)
        
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        return provider
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Patients
# ============================================================

@app.get(
    "/api/patients",
    response_model=List[Patient],
    tags=["Patients"],
    summary="List Patients",
    description="Get all patients"
)
async def get_patients():
    """Get all patients."""
    try:
        return json_client._load_json(json_client.patients_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/api/patients/{patient_id}",
    response_model=Patient,
    tags=["Patients"],
    summary="Get Patient",
    description="Get a specific patient by ID"
)
async def get_patient(patient_id: str):
    """Get a single patient by ID."""
    try:
        patient = json_client.get_patient(patient_id)
        
        if not patient:
            raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
        
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# Waitlist & Freed Slots
# ============================================================

@app.get(
    "/api/waitlist",
    tags=["Waitlist"],
    summary="Get Waitlist",
    description="Get all patients on the waitlist"
)
async def get_waitlist():
    """Get all waitlist entries."""
    try:
        waitlist_file = DATA_DIR / "waitlist.json"
        if waitlist_file.exists():
            with open(waitlist_file, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load waitlist: {str(e)}")

@app.get(
    "/api/freed-slots",
    tags=["Waitlist"],
    summary="Get Freed Slots",
    description="Get all available freed appointment slots"
)
async def get_freed_slots():
    """Get all freed slots available for backfilling."""
    try:
        slots_file = DATA_DIR / "freed_slots.json"
        if slots_file.exists():
            with open(slots_file, 'r') as f:
                slots = json.load(f)
                # Only return available slots
                return [s for s in slots if s.get('status') == 'available']
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load freed slots: {str(e)}")

# ============================================================
# Patient Response Simulation (for demo)
# ============================================================

# REMOVED: Duplicate /api/patient-response endpoint (demo version that didn't update database)
# The real functional endpoint is defined below (search for "Handle patient response")

# REMOVED: Duplicate POST /api/patient-response endpoint (demo version that didn't update database)

# ============================================================
# Appointment Management (UPDATE/CANCEL/REASSIGN)
# ============================================================

@app.put(
    "/api/appointments/{appointment_id}",
    tags=["Appointments"],
    summary="Update Appointment",
    description="Update appointment details (provider, date, time, status)"
)
async def update_appointment(appointment_id: str, updates: AppointmentUpdateRequest):
    """Update an appointment."""
    try:
        updates_dict = updates.dict(exclude_unset=True)
        success = json_client.update_appointment(appointment_id, updates_dict)
        
        if success:
            return {
                "success": True,
                "appointment_id": appointment_id,
                "updates": updates_dict,
                "message": "Appointment updated successfully"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/appointments/{appointment_id}/cancel",
    tags=["Appointments"],
    summary="Cancel Appointment",
    description="Cancel an appointment and trigger automatic backfill"
)
async def cancel_appointment(appointment_id: str):
    """Cancel an appointment and trigger automatic backfill."""
    try:
        # Load appointment data before cancelling
        appointments_file = DATA_DIR / "appointments.json"
        with open(appointments_file, 'r') as f:
            appointments = json.load(f)
        
        # Find the appointment
        appointment_to_cancel = None
        for apt in appointments:
            if apt.get('appointment_id') == appointment_id:
                appointment_to_cancel = apt.copy()
                apt['status'] = 'cancelled'
                apt['confirmation_status'] = 'cancelled'
                break
        
        if not appointment_to_cancel:
            raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
        
        # Save updated appointments
        with open(appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        patient_id = appointment_to_cancel.get('patient_id')
        
        # Add patient to waitlist and trigger backfill
        backfill_result = None
        try:
            from agents.backfill_agent import BackfillAgent
            from api.json_client import JSONClient
            
            json_client_instance = JSONClient()
            
            # Get patient details for waitlist
            patients_file = DATA_DIR / "patients.json"
            with open(patients_file, 'r') as f:
                patients = json.load(f)
            
            patient_data = next((p for p in patients if p.get('patient_id') == patient_id), None)
            
            if patient_data:
                # Create waitlist entry
                from datetime import datetime
                waitlist_entry = {
                    "patient_id": patient_id,
                    "name": patient_data.get('name', 'Unknown'),
                    "condition": patient_data.get('condition', 'Unknown'),
                    "no_show_risk": patient_data.get('no_show_risk', 0.5),
                    "priority": "HIGH",  # High priority since appointment was cancelled
                    "requested_specialty": "Physical Therapy",
                    "requested_location": patient_data.get('preferred_location', 'Any'),
                    "availability_windows": {
                        "days": patient_data.get('preferred_days', 'Monday,Tuesday,Wednesday,Thursday,Friday').split(','),
                        "times": ["Morning", "Afternoon"]
                    },
                    "insurance": patient_data.get('insurance_provider', 'Unknown'),
                    "current_appointment": None,
                    "willing_to_move_up": True,
                    "added_to_waitlist": datetime.utcnow().isoformat() + "Z",
                    "waitlist_reason": "Appointment cancelled by receptionist - needs reassignment",
                    "notes": "Appointment cancelled by receptionist - needs rescheduling"
                }
                
                # Add to waitlist
                json_client_instance.add_to_waitlist(waitlist_entry)
            
            # Trigger backfill
            backfill_agent = BackfillAgent(json_client_instance)
            backfill_result = backfill_agent.handle_slot_freed(
                appointment_to_cancel,
                reason="Appointment cancelled by receptionist - immediate backfill"
            )
            
            # Get patient name if backfilled
            if backfill_result and backfill_result.get('status') == 'BACKFILLED':
                backfilled_patient_id = backfill_result.get('patient_id')
                patients_file = DATA_DIR / "patients.json"
                with open(patients_file, 'r') as f:
                    patients = json.load(f)
                for p in patients:
                    if p.get('patient_id') == backfilled_patient_id:
                        backfill_result['patient_name'] = p.get('name', backfilled_patient_id)
                        break
                    
        except Exception as e:
            print(f"[CANCEL] Backfill error: {str(e)}")
            # Continue without failing - appointment still cancelled
            backfill_result = {"status": "ERROR", "message": str(e)}
        
        return {
            "success": True,
            "appointment_id": appointment_id,
            "patient_id": patient_id,
            "status": "cancelled",
            "message": "Appointment cancelled successfully",
            "backfill_result": backfill_result
        }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
    "/api/appointments/{appointment_id}/reassign",
    tags=["Appointments"],
    summary="Reassign Appointment",
    description="Reassign an appointment to a new provider"
)
async def reassign_appointment(appointment_id: str, request: AppointmentReassignRequest):
    """Reassign an appointment to a new provider."""
    try:
        success = json_client.reassign_appointment(
            appointment_id=appointment_id,
            new_provider_id=request.new_provider_id,
            reason=request.reason
        )
        
        if success:
            return {
                "success": True,
                "appointment_id": appointment_id,
                "new_provider_id": request.new_provider_id,
                "status": "rescheduled",
                "message": f"Appointment reassigned to {request.new_provider_id}"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Workflow Trigger Endpoint
# ============================================================

class WorkflowTriggerRequest(BaseModel):
    trigger_type: str  # provider_unavailable, patient_request, etc.
    provider_id: Optional[str] = None
    patient_id: Optional[str] = None
    reason: Optional[str] = None
    date: Optional[str] = None  # Deprecated: use start_date/end_date
    start_date: Optional[str] = None  # NEW: Start date for range
    end_date: Optional[str] = None    # NEW: End date for range
    metadata: Optional[dict] = None


@app.post(
    "/api/trigger-workflow",
    tags=["Workflow"],
    summary="Trigger AI Workflow",
    description="Trigger the AI workflow for provider unavailability or other events"
)
async def trigger_workflow(request: WorkflowTriggerRequest):
    """
    Trigger the AI workflow to handle provider unavailability,
    patient rescheduling, or other workflow events.
    
    🚀 NOW USING TEMPLATE-DRIVEN ORCHESTRATOR (Your idea!)
    - Fetches all data upfront
    - Pre-calculates match scores
    - ONE LLM call with template variables
    - 5x faster, 80% cheaper than tool calling
    """
    try:
        # Import workflow components (TEMPLATE-DRIVEN!)
        from workflows.template_driven_orchestrator import create_template_driven_orchestrator
        from agents.smart_scheduling_agent import SmartSchedulingAgent
        from agents.patient_engagement_agent import PatientEngagementAgent
        from mcp_servers.domain.json_server import JSONDomainServer
        
        # Simple BookingAgent wrapper
        class BookingAgent:
            def __init__(self, domain_server):
                self.domain = domain_server
            
            def book_appointment(self, appointment_id, provider_id, status=None, match_score=None, match_factors=None, match_quality=None, reasoning=None):
                """Book an appointment with optional status override and match metadata."""
                try:
                    print(f"[DEBUG] BookingAgent.book_appointment called:")
                    print(f"  appointment_id={appointment_id}, provider_id={provider_id}")
                    print(f"  match_score={match_score}, match_factors={type(match_factors) if match_factors else None}")
                    print(f"  match_quality={match_quality}, reasoning={reasoning[:50] if reasoning else None}...")
                    
                    appointments = self.domain.json_client._load_json(self.domain.json_client.appointments_file)
                    for apt in appointments:
                        if apt.get('appointment_id') == appointment_id:
                            apt['provider_id'] = provider_id
                            apt['status'] = status if status else 'rescheduled'
                            apt['reassigned'] = True
                            apt['confirmation_status'] = 'needs_review' if status == 'needs_review' else 'pending'
                            
                            # Store match metadata for UI tooltips
                            if match_score is not None:
                                apt['match_score'] = match_score
                                print(f"  ✅ Stored match_score: {match_score}")
                            if match_factors is not None:
                                apt['match_factors'] = match_factors
                                print(f"  ✅ Stored match_factors: {list(match_factors.keys()) if isinstance(match_factors, dict) else match_factors}")
                            if match_quality is not None:
                                apt['match_quality'] = match_quality
                                print(f"  ✅ Stored match_quality: {match_quality}")
                            if reasoning is not None:
                                apt['reasoning'] = reasoning
                                print(f"  ✅ Stored reasoning: {reasoning[:50]}...")
                            
                            # Update in JSON
                            self.domain.json_client._save_json(self.domain.json_client.appointments_file, appointments)
                            return True
                    return False
                except Exception as e:
                    print(f"[ERROR] BookingAgent.book_appointment: {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        
        # Initialize components
        domain_server = JSONDomainServer()
        
        # Use REAL LLM - agents will auto-configure LiteLLM or fall back to mock
        # This allows the template-driven orchestrator to use actual AI reasoning!
        smart_scheduling_agent = SmartSchedulingAgent(
            domain_server=domain_server
            # No llm parameter - uses default (LiteLLM if available, mock as fallback)
        )
        patient_engagement_agent = PatientEngagementAgent(
            domain_server=domain_server
            # No llm parameter - uses default (LiteLLM if available, mock as fallback)
        )
        booking_agent = BookingAgent(domain_server)
        
        # Create TEMPLATE-DRIVEN orchestrator with REAL LLM
        orchestrator = create_template_driven_orchestrator(
            domain_server=domain_server,
            smart_scheduling_agent=smart_scheduling_agent,
            patient_engagement_agent=patient_engagement_agent,
            booking_agent=booking_agent,
            llm=None,  # None = uses default LiteLLM (will auto-fallback to mock if LiteLLM fails)
            use_langfuse=False  # Use local template for now, can enable later
        )
        
        # Prepare input based on trigger type
        if request.trigger_type == "provider_unavailable":
            # Support date range (start_date/end_date) or single date (backward compatibility)
            start_date = request.start_date or request.date or datetime.now().date().isoformat()
            end_date = request.end_date or start_date
            
            # Execute template-driven workflow with date range
            result = orchestrator.execute_workflow(
                provider_id=request.provider_id,
                start_date=start_date,
                end_date=end_date,
                reason=request.reason or "unavailable"
            )
            
            # Calculate emails sent (one per assignment)
            emails_sent = result.get("successful_assignments", 0)
            
            # Determine which method was used
            assignment_method = result.get("assignment_method", "llm-template-driven")
            used_fallback = result.get("used_fallback", False)
            
            # Create descriptive message
            if used_fallback:
                method_msg = "🔄 Rule-based assignment (LLM fallback)"
                workflow_type = "provider_unavailable (RULE-BASED FALLBACK)"
            else:
                method_msg = "🤖 AI-powered template-driven assignment"
                workflow_type = "provider_unavailable (TEMPLATE-DRIVEN AI)"
            
            return {
                "success": True,
                "workflow_type": workflow_type,
                "assignment_method": assignment_method,
                "used_fallback": used_fallback,
                "provider_id": request.provider_id,
                "affected_appointments_count": result.get("total_affected", 0),
                "assignments": result.get("assignments", []),
                "emails_sent": emails_sent,
                "waitlist_count": result.get("waitlist_entries", 0),
                "message": f"✅ {method_msg}: {result.get('total_affected', 0)} appointments processed",
                "details": result,
                # Include metadata for audit log
                "metadata": result.get("metadata", {})
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported trigger type: {request.trigger_type}"
            )
            
    except ImportError as e:
        # Fallback if workflow modules not available
        return {
            "success": False,
            "error": "Workflow system not available",
            "message": "Please use the chat UI at http://localhost:8501/ to trigger workflows",
            "details": str(e)
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


# ============================================================
# Patient Response Endpoints (Accept/Decline)
# ============================================================

@app.get(
    "/api/patient-response",
    tags=["Patient"],
    summary="Patient Accept/Decline Response",
    description="Handle patient response to provider reassignment offer"
)
async def patient_response(token: str, response: str):
    """Handle patient response (accept/decline) to reassignment offer."""
    try:
        # Parse token: appointment_id_patient_id_provider_id
        parts = token.split('_')
        if len(parts) < 3:
            return HTMLResponse("""
                <html><body style="font-family: Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #e74c3c;">❌ Invalid Link</h1>
                    <p>This confirmation link is invalid.</p>
                </body></html>
            """)
        
        appointment_id = parts[0]
        patient_id = parts[1]
        provider_id = parts[2]
        
        # Load emails
        emails_file = DATA_DIR / "emails.json"
        if emails_file.exists():
            with open(emails_file, 'r') as f:
                emails = json.load(f)
        else:
            emails = []
        
        # Find and update email
        email_found = False
        for email in emails:
            if email.get('id') == token:
                email['status'] = 'accepted' if response == 'accept' else 'declined'
                email['responded_at'] = datetime.now().isoformat()
                email_found = True
                break
        
        # Save updated emails
        if email_found:
            with open(emails_file, 'w') as f:
                json.dump(emails, f, indent=2)
        
        # If accepted, update appointment
        if response == 'accept':
            # Load appointments directly from JSON file
            appointments_file = DATA_DIR / "appointments.json"
            with open(appointments_file, 'r') as f:
                appointments = json.load(f)
            
            # Update appointment status
            for apt in appointments:
                if apt.get('appointment_id') == appointment_id:
                    apt['provider_id'] = provider_id
                    apt['status'] = 'confirmed'
                    apt['confirmation_status'] = 'confirmed'
                    apt['reassigned'] = True
                    break
            
            # Save updated appointments back to file
            with open(appointments_file, 'w') as f:
                json.dump(appointments, f, indent=2)
            
            return HTMLResponse(f"""
                <html><body style="font-family: Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #27ae60;">✅ Appointment Confirmed!</h1>
                    <p style="font-size: 18px;">Thank you for confirming your appointment.</p>
                    <p>Appointment ID: <strong>{appointment_id}</strong></p>
                    <p style="margin-top: 30px; color: #7f8c8d;">You can close this window.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body></html>
            """)
        else:
            # If declined, trigger automatic backfill
            appointments_file = DATA_DIR / "appointments.json"
            with open(appointments_file, 'r') as f:
                appointments = json.load(f)
            
            # Find the appointment before updating
            declined_appointment = None
            for apt in appointments:
                if apt.get('appointment_id') == appointment_id:
                    declined_appointment = apt.copy()  # Keep original for backfill
                    apt['status'] = 'cancelled'
                    apt['confirmation_status'] = 'declined'
                    break
            
            # Save updated appointments back to file
            with open(appointments_file, 'w') as f:
                json.dump(appointments, f, indent=2)
            
            # NEW: Trigger automatic backfill
            backfill_message = ""
            if declined_appointment:
                try:
                    from agents.backfill_agent import BackfillAgent
                    from api.json_client import JSONClient
                    
                    backfill_agent = BackfillAgent(JSONClient())
                    
                    # Add patient to waitlist first
                    json_client = JSONClient()
                    patient_data = json_client.get_patient(patient_id)
                    waitlist_entry = {
                        "patient_id": patient_id,
                        "name": patient_data.get('name', patient_id),
                        "condition": patient_data.get('condition', 'N/A'),
                        "no_show_risk": patient_data.get('no_show_risk', 0.5),
                        "priority": "HIGH",
                        "requested_specialty": patient_data.get('condition_specialty_required', 'Physical Therapy'),
                        "requested_location": patient_data.get('preferred_location', 'Any'),
                        "availability_windows": {
                            "days": patient_data.get('preferred_days', '').split(',') if patient_data.get('preferred_days') else ['Any'],
                            "times": ["Morning", "Afternoon"]
                        },
                        "insurance": patient_data.get('insurance_provider', 'Unknown'),
                        "current_appointment": appointment_id,
                        "willing_to_move_up": True,
                        "added_to_waitlist": datetime.now().isoformat() + "Z",
                        "waitlist_reason": "Patient declined the reassignment offer - exploring alternatives",
                        "notes": "Patient declined reassignment offer"
                    }
                    json_client.add_to_waitlist(waitlist_entry)
                    
                    # Try to backfill the freed slot
                    backfill_result = backfill_agent.handle_slot_freed(
                        declined_appointment,
                        reason="Patient declined reassignment offer"
                    )
                    
                    if backfill_result.get('status') == 'BACKFILLED':
                        backfilled_patient = backfill_result.get('patient_id')
                        backfill_message = f"<p style='color: #27ae60; margin-top: 20px;'>✨ Good news! We found another patient for this time slot.</p>"
                    else:
                        backfill_message = f"<p style='color: #7f8c8d; margin-top: 20px;'>You've been added to our priority waitlist.</p>"
                        
                except Exception as e:
                    print(f"[BACKFILL ERROR] {str(e)}")
                    # Continue without failing - patient still gets decline confirmation
                    backfill_message = "<p style='color: #7f8c8d; margin-top: 20px;'>You've been added to our waitlist.</p>"
            
            return HTMLResponse(f"""
                <html><body style="font-family: Arial; padding: 40px; text-align: center;">
                    <h1 style="color: #e67e22;">📋 Request Noted</h1>
                    <p style="font-size: 18px;">We've noted that you declined this appointment.</p>
                    <p>Our team will contact you to find an alternative.</p>
                    {backfill_message}
                    <p>Appointment ID: <strong>{appointment_id}</strong></p>
                    <p style="margin-top: 30px; color: #7f8c8d;">You can close this window.</p>
                    <script>setTimeout(() => window.close(), 3000);</script>
                </body></html>
            """)
        
    except Exception as e:
        return HTMLResponse(f"""
            <html><body style="font-family: Arial; padding: 40px; text-align: center;">
                <h1 style="color: #e74c3c;">❌ Error</h1>
                <p>An error occurred: {str(e)}</p>
            </body></html>
        """)


@app.get(
    "/api/emails",
    tags=["Emails"],
    summary="Get All Emails",
    description="Retrieve all sent emails for demo viewing"
)
async def get_emails():
    """Get all sent emails from the JSON file."""
    try:
        emails_file = DATA_DIR / "emails.json"
        if emails_file.exists():
            with open(emails_file, 'r') as f:
                emails = json.load(f)
            return emails
        return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load emails: {str(e)}")


# ============================================================
# Demo Reset Endpoint
# ============================================================

class DemoResetRequest(BaseModel):
    start_date: Optional[str] = None  # YYYY-MM-DD, defaults to today
    days_ahead: int = 7  # Number of days to create appointments for
    providers: Optional[List[str]] = None  # List of provider IDs, defaults to all
    appointments_per_day: int = 3  # Number of appointments to create per day (default 3 for testing)

@app.post(
    "/api/demo/reset",
    tags=["Demo"],
    summary="Reset Demo Data",
    description="Reset appointments for demo - creates fresh appointments for date range (weekdays only, future times only)"
)
async def reset_demo(request: DemoResetRequest):
    """
    Reset demo data by recreating appointments for specified date range.
    
    - Creates appointments only on weekdays (Mon-Fri)
    - Skips times that have already passed today
    - Distributes patients across providers
    - Clears emails and waitlist
    """
    try:
        from datetime import datetime, timedelta
        import random
        
        # Parse start date or use today
        if request.start_date:
            start_date = datetime.strptime(request.start_date, "%Y-%m-%d")
        else:
            start_date = datetime.now()
        
        # Load data files
        providers_file = DATA_DIR / "providers.json"
        seed_file = DATA_DIR / "demo_seed_appointments.json"
        appointments_file = DATA_DIR / "appointments.json"
        emails_file = DATA_DIR / "emails.json"
        waitlist_file = DATA_DIR / "waitlist.json"
        freed_slots_file = DATA_DIR / "freed_slots.json"
        
        with open(providers_file, 'r') as f:
            providers = json.load(f)
        with open(seed_file, 'r') as f:
            seed_data = json.load(f)
        
        realistic_patients = seed_data['realistic_appointments']
        provider_specialty_map = seed_data['provider_specialty_mapping']
        
        # Filter providers if specified
        if request.providers:
            providers = [p for p in providers if p['provider_id'] in request.providers]
        
        # Time slots (30-minute intervals)
        time_slots = [
            "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "13:00", "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"
        ]
        
        # Generate appointments using realistic patient-provider matching
        appointments = []
        appointment_counter = 1
        current_time = datetime.now()
        
        for day_offset in range(request.days_ahead):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() >= 5:
                continue
            
            # Track used slots per provider to avoid overlaps
            provider_slots_used = {p['provider_id']: set() for p in providers}
            appointments_for_day = 0
            patient_index = 0
            
            # Create specified number of appointments per day
            while appointments_for_day < request.appointments_per_day:
                # Get patient (cycle through realistic patients)
                if patient_index >= len(realistic_patients):
                    patient_index = 0
                patient_data = realistic_patients[patient_index]
                patient_index += 1
                
                # Skip waitlist patients for regular appointments
                if patient_data['match_type'] == 'waitlist':
                    continue
                
                # Match patient to appropriate provider based on specialty
                matched_provider = None
                for provider in providers:
                    if provider_specialty_map.get(provider['provider_id']) == patient_data['specialty_needed']:
                        matched_provider = provider
                        break
                
                # If no perfect match, use first available provider
                if not matched_provider and providers:
                    matched_provider = providers[0]
                
                if matched_provider:
                    # Find available time slot for this provider
                    available_slot = None
                    for time_slot in time_slots:
                        # Skip past times if it's today
                        if current_date.date() == current_time.date():
                            slot_time = datetime.strptime(time_slot, "%H:%M").time()
                            if slot_time <= current_time.time():
                                continue
                        
                        # Check if slot is available for this provider
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
                    else:
                        # No more slots available for this provider, try next patient
                        break
        
        # Save appointments
        with open(appointments_file, 'w') as f:
            json.dump(appointments, f, indent=2)
        
        # Clear emails
        with open(emails_file, 'w') as f:
            json.dump([], f, indent=2)
        
        # Clear waitlist
        with open(waitlist_file, 'w') as f:
            json.dump([], f, indent=2)
        
        # Clear freed slots
        with open(freed_slots_file, 'w') as f:
            json.dump([], f, indent=2)
        
        # Reset provider unavailable dates
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
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to reset demo: {str(e)}")


# ============================================================
# Run Server
# ============================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🏥 Healthcare Operations Assistant API")
    print("="*60)
    print(f"\nStarting server...")
    print(f"  📋 API:        http://localhost:8000")
    print(f"  📚 Swagger:    http://localhost:8000/docs")
    print(f"  📖 ReDoc:      http://localhost:8000/redoc")
    print(f"  🔍 OpenAPI:    http://localhost:8000/openapi.json")
    print("\n" + "="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
