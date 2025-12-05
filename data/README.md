# Data Files - Simple JSON Storage

These JSON files store your appointment, provider, and patient data.

## Files

- **appointments.json** - All appointments (3 currently scheduled for T001)
- **providers.json** - All providers (T001 is marked as "sick")
- **patients.json** - All patients

## How to Use Real Data

### Current Setup (Mocked)
```python
# orchestrator/workflow.py
from mcp_servers.domain.server import create_domain_server  # ← MOCKED data
```

### Switch to Real JSON Data (ONE LINE CHANGE)
```python
# orchestrator/workflow.py
from mcp_servers.domain.json_server import create_json_domain_server as create_domain_server  # ← REAL data!
```

That's it! Now when you type "therapist departed T001", it will:
- ✅ Query **real appointments from JSON file**
- ✅ Find **real providers from JSON file**  
- ✅ Get **real patient data from JSON file**

## How to Add More Data

Just edit the JSON files! For example, to add more appointments:

```json
// appointments.json
[
  {
    "appointment_id": "A004",
    "patient_id": "PAT004",
    "provider_id": "T001",
    "date": "2024-11-23",
    "time": "11:00 AM",
    "status": "scheduled",
    "confirmation_number": "CONF-004"
  }
]
```

## Testing

Test the data connection:
```bash
# Test JSON client
python api/json_client.py

# Test domain server
python mcp_servers/domain/json_server.py
```

## Next Steps

Later, you can swap JSON files for:
- **WebPT API** - Connect to real EMR system
- **Database** - PostgreSQL, MySQL, etc.
- **Google Sheets** - For easy editing in spreadsheet

Just change ONE LINE in workflow.py - the rest stays the same!

