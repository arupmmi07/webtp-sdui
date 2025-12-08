"""Simple web server to serve HTML pages for deployment.

This replaces the complex Streamlit setup with a simple server that just serves HTML files.
Perfect for deployment where we only need the HTML pages (schedule, emails, reset).
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import os

# Create FastAPI app
app = FastAPI(
    title="WebTP Demo UI",
    description="Simple web server for HTML pages",
    version="1.0.0"
)

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
                    <a href="/schedule.html" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📅</span>
                            <span class="url-title">Appointment Schedule</span>
                        </div>
                        <div class="url-path">/schedule.html</div>
                        <div class="url-desc">Interactive calendar showing all appointments, provider availability, and real-time scheduling</div>
                    </a>
                    
                    <a href="/emails.html" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📧</span>
                            <span class="url-title">Patient Emails</span>
                        </div>
                        <div class="url-path">/emails.html</div>
                        <div class="url-desc">View AI-generated patient communications, confirmations, and rescheduling notifications</div>
                    </a>
                    
                    <a href="/reset.html" class="url-card">
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
                    <a href="/docs" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📖</span>
                            <span class="url-title">Interactive API Docs</span>
                        </div>
                        <div class="url-path">/docs</div>
                        <div class="url-desc">Swagger UI with interactive API testing, request/response examples, and endpoint documentation</div>
                    </a>
                    
                    <a href="/redoc" class="url-card">
                        <div class="url-header">
                            <span class="url-icon">📋</span>
                            <span class="url-title">ReDoc Documentation</span>
                        </div>
                        <div class="url-path">/redoc</div>
                        <div class="url-desc">Clean, readable API documentation with detailed schemas and examples</div>
                    </a>
                    
                    <a href="/openapi.json" class="url-card">
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
                    <a href="/health" class="url-card">
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
