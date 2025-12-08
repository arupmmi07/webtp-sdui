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

@app.post("/api/demo/reset")
async def reset_demo_data(request: DemoResetRequest):
    """Reset demo data with realistic appointments."""
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
                realistic_patients = json.load(f)
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
        
        for day_offset in range(request.days_ahead):
            current_date = start_date + timedelta(days=day_offset)
            
            # Skip weekends
            if current_date.weekday() >= 5:
                continue
            
            # Track used slots per provider to avoid overlaps
            provider_slots_used = {p['provider_id']: set() for p in providers}
            appointments_for_day = 0
            patient_index = 0
            
            while appointments_for_day < request.appointments_per_day:
                if patient_index >= len(realistic_patients):
                    patient_index = 0
                patient_data = realistic_patients[patient_index]
                patient_index += 1
                
                # Skip waitlist patients for regular appointments
                if patient_data.get('match_type') == 'waitlist':
                    continue
                
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
                    else:
                        break
        
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
                    
                    <a href="/reset.html" target="_blank" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">🔄</span>
                            <span class="url-title">Demo Reset Control</span>
                        </div>
                        <div class="url-path">/reset.html</div>
                        <div class="url-desc">Reset demo data, generate realistic appointments, and control demo scenarios</div>
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

@app.get("/reset.html", response_class=FileResponse)
async def get_reset():
    """Serve reset HTML page."""
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
