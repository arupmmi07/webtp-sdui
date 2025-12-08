# Windows PowerShell deployment script for GCP VMs

Write-Host "🚀 Deploying WebTP Demo on Windows..." -ForegroundColor Green

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Install Python 3.11+ from https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green

# Check pip
if (!(Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pip not found" -ForegroundColor Red
    exit 1
}
Write-Host "✅ pip found" -ForegroundColor Green

# Install dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Get VM IP
$ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*"} | Select-Object -First 1).IPAddress

# Set environment variables
Write-Host "`nSetting environment variables..." -ForegroundColor Yellow
$env:APP_BASE_URL = "http://${ip}:8000"

# Check for Azure credentials
if (!$env:AZURE_API_KEY) {
    Write-Host "⚠️  AZURE_API_KEY not set" -ForegroundColor Yellow
}
if (!$env:AZURE_API_BASE) {
    Write-Host "⚠️  AZURE_API_BASE not set" -ForegroundColor Yellow
}
if (!$env:AZURE_DEPLOYMENT_NAME) {
    Write-Host "⚠️  AZURE_DEPLOYMENT_NAME not set" -ForegroundColor Yellow
}

# Create logs directory
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
}

# Start API server
Write-Host "`nStarting API server on port 8000..." -ForegroundColor Yellow
Start-Process python -ArgumentList "api/server.py" -NoNewWindow -RedirectStandardOutput "logs/api.log" -RedirectStandardError "logs/api_error.log"

Start-Sleep -Seconds 2

# Test if server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    Write-Host "`n✅ Deployed successfully!" -ForegroundColor Green
    Write-Host "`n📍 Access URLs:" -ForegroundColor Cyan
    Write-Host "   Schedule: http://${ip}:8000/schedule.html"
    Write-Host "   Emails:   http://${ip}:8000/emails.html"
    Write-Host "   API Docs: http://${ip}:8000/docs"
} catch {
    Write-Host "`n❌ Server failed to start. Check logs/api_error.log" -ForegroundColor Red
}

