# REST API Server

Simple REST API that exposes appointment, provider, and patient data from JSON files.

## Quick Start

```bash
# Start API + UI together
make dev

# Or run API only
python3 api/server.py
```

The API will be available at: **http://localhost:8000**

## Endpoints

### Health Check
```bash
GET /health
```

### Appointments
```bash
# Get all appointments for a provider
GET /api/appointments?provider_id=T001&status=scheduled

# Get single appointment
GET /api/appointments/A001

# Book appointment
POST /api/appointments/book
Content-Type: application/json

{
  "appointment_id": "A004",
  "patient_id": "PAT001",
  "provider_id": "P001",
  "date": "2024-11-23",
  "time": "10:00 AM",
  "status": "scheduled"
}
```

### Providers
```bash
# Get all active providers
GET /api/providers?status=active

# Get single provider
GET /api/providers/P001
```

### Patients
```bash
# Get single patient
GET /api/patients/PAT001
```

## Test with curl

```bash
# Test health
curl http://localhost:8000/health

# Get appointments for T001
curl "http://localhost:8000/api/appointments?provider_id=T001"

# Get all providers
curl http://localhost:8000/api/providers

# Get specific patient
curl http://localhost:8000/api/patients/PAT001
```

## Data Source

The API reads from JSON files in `data/` folder:
- `data/appointments.json`
- `data/providers.json`
- `data/patients.json`

Edit these files to change the data!

