#!/usr/bin/env python3
"""Simple Web Server for HTML Pages - Streamlit Replacement.

This replaces the Streamlit chat UI with a simple FastAPI server that serves HTML pages.
Uses the same file structure so DevOps doesn't need to change deployment scripts.

Usage:
    streamlit run demo/chat_ui.py  (will actually run FastAPI server)
    python demo/chat_ui.py

Features:
    - Serves static HTML pages (schedule, emails, reset)
    - Same entry point as Streamlit
    - Compatible with existing deployment
"""

import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the web server
from web_server import app
import uvicorn

def main():
    """Main entry point - runs the web server instead of Streamlit."""
    port = int(os.getenv("PORT", 8501))  # Use 8501 to match Streamlit default
    
    print("🌐 Starting WebPT Demo UI (HTML Server)")
    print("=" * 50)
    print(f"📱 Access at: http://localhost:{port}")
    print(f"📅 Schedule: http://localhost:{port}/schedule.html")
    print(f"📧 Emails: http://localhost:{port}/emails.html")
    print(f"🔄 Reset: http://localhost:{port}/reset.html")
    print("=" * 50)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()