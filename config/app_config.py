"""Application configuration for domain/URL management."""

import os

# Base URL configuration
# Set APP_BASE_URL environment variable when deploying to Azure
# Example: https://webpt-demo.azurewebsites.net
BASE_URL = os.getenv("APP_BASE_URL", "http://localhost:8000")

# API endpoints
API_BASE = f"{BASE_URL}/api"

# UI endpoints
SCHEDULE_URL = f"{BASE_URL}/schedule.html"
EMAILS_URL = f"{BASE_URL}/emails.html"
API_DOCS_URL = f"{BASE_URL}/docs"

# Email link generation (for patient accept/decline links)
def get_patient_response_url(token: str, response: str) -> str:
    """Generate patient response URL with correct domain."""
    return f"{BASE_URL}/api/patient-response?token={token}&response={response}"

def get_email_accept_url(token: str) -> str:
    """Generate email accept URL."""
    return get_patient_response_url(token, "accept")

def get_email_decline_url(token: str) -> str:
    """Generate email decline URL."""
    return get_patient_response_url(token, "decline")

# Health check
def get_health_url() -> str:
    """Get health check URL."""
    return f"{BASE_URL}/health"

