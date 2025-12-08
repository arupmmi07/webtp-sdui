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
    """Landing page with navigation to all HTML pages."""
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>WebTP Demo</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                text-align: center;
                max-width: 600px;
                width: 100%;
            }
            h1 {
                color: #2c3e50;
                margin-bottom: 10px;
                font-size: 2.5rem;
            }
            .subtitle {
                color: #7f8c8d;
                margin-bottom: 40px;
                font-size: 1.1rem;
            }
            .nav-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .nav-card {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 30px 20px;
                text-decoration: none;
                color: #2c3e50;
                transition: all 0.3s;
                display: block;
            }
            .nav-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 10px 25px rgba(0,0,0,0.1);
                border-color: #667eea;
            }
            .nav-icon {
                font-size: 2.5rem;
                margin-bottom: 15px;
                display: block;
            }
            .nav-title {
                font-weight: 600;
                margin-bottom: 8px;
                font-size: 1.1rem;
            }
            .nav-desc {
                color: #6c757d;
                font-size: 0.9rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏥 WebTP Demo</h1>
            <p class="subtitle">Physical Therapy Scheduling & AI Assistant</p>
            
            <div class="nav-grid">
                <a href="/schedule.html" class="nav-card">
                    <span class="nav-icon">📅</span>
                    <div class="nav-title">Schedule</div>
                    <div class="nav-desc">View appointment calendar</div>
                </a>
                
                <a href="/emails.html" class="nav-card">
                    <span class="nav-icon">📧</span>
                    <div class="nav-title">Emails</div>
                    <div class="nav-desc">Patient communications</div>
                </a>
                
                <a href="/reset.html" class="nav-card">
                    <span class="nav-icon">🔄</span>
                    <div class="nav-title">Reset</div>
                    <div class="nav-desc">Demo data control</div>
                </a>
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
