# Mocked Components Tracker

## Status Legend
- 🟡 MOCKED - Using hardcoded/fake implementation
- 🟢 REAL - Using actual service/implementation
- 🔴 TODO - Not implemented yet

---

## Components Status

| Component | Status | Mock Implementation | Real Implementation | Swap Priority | Estimated Effort |
|-----------|--------|-------------------|-------------------|---------------|------------------|
| **LLM Calls** | 🟡 MOCKED | `adapters/llm/mock_llm.py` | `adapters/llm/litellm_adapter.py` | HIGH | 2 hours |
| **LangFuse Prompts** | 🟡 MOCKED | Hardcoded in mock_llm.py | Pull from LangFuse API | HIGH | 2 hours |
| **Knowledge Files** | 🟡 MOCKED | .txt files with rules | .pdf files | MEDIUM | 1 hour |
| **MCP Knowledge Server** | 🟡 MOCKED | Returns hardcoded rules | Parse PDFs dynamically | MEDIUM | 4 hours |
| **MCP Domain Server** | 🟡 MOCKED | Returns hardcoded data | Connect to DB/API | LOW | 8 hours |
| **SMS/Email** | 🟡 MOCKED | Print to console | Twilio/SendGrid | LOW | 4 hours |
| **Event Queue** | 🟢 REAL | Python Queue | Python Queue | N/A | Done |
| **Workflow** | 🟢 REAL | LangGraph | LangGraph | N/A | Done |

---

## Mock Details

### 1. Mock LLM (`adapters/llm/mock_llm.py`)

**What it mocks:** Anthropic Claude API calls via LiteLLM

**Current behavior:**
- Filtering: Returns hardcoded `["P001", "P004"]` (eliminates P003 for location)
- Scoring: Returns hardcoded `{"P001": 75, "P004": 40}`
- All decisions are deterministic and predictable

**How to swap to real:**
```python
# Step 1: Ensure you have API keys
export ANTHROPIC_API_KEY="your-key"
export LANGFUSE_PUBLIC_KEY="your-key"
export LANGFUSE_SECRET_KEY="your-key"

# Step 2: Change one line in your agent initialization
# Before (Mock):
from adapters.llm.mock_llm import MockLLM
llm = MockLLM()

# After (Real):
from adapters.llm.litellm_adapter import LiteLLMAdapter
llm = LiteLLMAdapter(model="claude-sonnet-4")
```

**Testing:**
```bash
# Run with mocks (no API calls)
python demo/cli.py

# Run with real LLM (requires API keys)
python demo/cli.py --real-llm
```

---

### 2. Mock LangFuse Prompts

**What it mocks:** LangFuse prompt management and versioning

**Current behavior:**
- Prompts are hardcoded strings in `mock_llm.py`
- No versioning, no A/B testing
- Prompts:
  - `provider_filtering`: "Apply these filters: {filters}..."
  - `provider_scoring`: "Score these providers: {providers}..."

**How to swap to real:**
```python
# Step 1: Create prompts in LangFuse dashboard
# - Go to https://cloud.langfuse.com
# - Create prompt "provider_filtering_v1"
# - Create prompt "provider_scoring_v1"

# Step 2: Update mock_llm.py
# Before (Mock):
def get_prompt_from_langfuse(self, prompt_name: str) -> str:
    prompts = {"provider_filtering": "Apply these filters..."}
    return prompts.get(prompt_name)

# After (Real):
from langfuse import Langfuse
langfuse_client = Langfuse()

def get_prompt_from_langfuse(self, prompt_name: str) -> str:
    prompt = langfuse_client.get_prompt(prompt_name)
    return prompt.compile()
```

---

### 3. Mock MCP Knowledge Server

**What it mocks:** PDF parsing and knowledge retrieval

**Current behavior:**
- Reads simple .txt files from `knowledge/sources/`
- Returns hardcoded rule dictionaries
- No semantic search, just keyword matching

**File structure (mocked):**
```
knowledge/sources/
├── clinic/
│   ├── scheduling_policy.txt  (simple text)
│   └── scoring_weights.txt    (simple text)
└── payers/
    └── medicare_rules.txt     (simple text)
```

**How to swap to real:**

**Step 1: Convert .txt → .pdf**
```bash
# Create real PDF files with proper formatting
# Or download actual CMS/insurance PDFs
```

**Step 2: Add PDF parsing**
```python
# Update mcp_servers/knowledge/server.py

# Before (Mock):
def search_knowledge(self, query: str) -> str:
    if "filter" in query:
        return "Hardcoded rules..."

# After (Real):
import pdfplumber

def search_knowledge(self, query: str) -> str:
    # Parse PDFs dynamically
    with pdfplumber.open("knowledge/sources/clinic/scheduling_policy.pdf") as pdf:
        text = "".join([page.extract_text() for page in pdf.pages])
        # Use LLM to extract relevant sections
        relevant = llm.extract_relevant(text, query)
        return relevant
```

**Step 3: Optional - Add Vector DB**
```python
# For semantic search over many PDFs
from pinecone import Pinecone

pc = Pinecone(api_key="your-key")
index = pc.Index("knowledge-base")

def search_knowledge(self, query: str) -> str:
    # Semantic search
    results = index.query(query, top_k=3)
    return results
```

---

### 4. Mock MCP Domain Server

**What it mocks:** Database/API calls for patient, provider, appointment data

**Current behavior:**
- Returns hardcoded dictionaries from `mcp_servers/domain/mock_responses.py`
- Data for:
  - 1 patient (Maria Rodriguez)
  - 3 providers (P001, P004, P003)
  - 1 appointment (A001)

**How to swap to real:**

**Option A: Connect to Database**
```python
# Update mcp_servers/domain/server.py

# Before (Mock):
MOCK_PROVIDERS = {"P001": {...}}
def get_provider(self, provider_id: str) -> dict:
    return MOCK_PROVIDERS.get(provider_id)

# After (Real with Supabase):
from supabase import create_client
supabase = create_client(url, key)

def get_provider(self, provider_id: str) -> dict:
    response = supabase.table("providers").select("*").eq("id", provider_id).execute()
    return response.data[0] if response.data else {}
```

**Option B: Connect to WebPT API**
```python
import requests

def get_provider(self, provider_id: str) -> dict:
    response = requests.get(
        f"https://api.webpt.com/v1/providers/{provider_id}",
        headers={"Authorization": f"Bearer {WEBPT_API_KEY}"}
    )
    return response.json()
```

---

### 5. Mock SMS/Email Communication

**What it mocks:** Twilio (SMS) and SendGrid (Email)

**Current behavior:**
- Prints to console: `[SMS] Offer sent to PAT001...`
- Always returns "YES" (patient accepts)

**How to swap to real:**

**SMS (Twilio):**
```python
# Before (Mock):
def send_sms(self, phone: str, message: str) -> str:
    print(f"[SMS] {message}")
    return "YES"

# After (Real):
from twilio.rest import Client
client = Client(account_sid, auth_token)

def send_sms(self, phone: str, message: str) -> str:
    message = client.messages.create(
        body=message,
        from_="+1234567890",
        to=phone
    )
    return message.sid
```

**Email (SendGrid):**
```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_email(self, to: str, subject: str, body: str):
    message = Mail(from_email="noreply@metropt.com", to_emails=to, subject=subject, html_content=body)
    sg = SendGridAPIClient(api_key)
    response = sg.send(message)
    return response.status_code
```

---

## Swap Sequence (Recommended Order)

### Phase 1: Validate Mocked Flow (Days 1-3)
✅ Implement all mocks  
✅ Test complete workflow  
✅ Verify architecture works  

### Phase 2: Core Services (Day 4)
**Priority: HIGH - Swap these first for realistic demo**

1. **Swap Mock LLM → LiteLLM** (2 hours)
   - File: `agents/smart_scheduling_agent.py`
   - Change: `MockLLM()` → `LiteLLMAdapter()`
   - Test: Verify real LLM decisions match expected logic

2. **Swap Mock Prompts → LangFuse** (2 hours)
   - Create prompts in LangFuse dashboard
   - Update: `mock_llm.py` to call LangFuse API
   - Test: Verify prompts load from LangFuse

### Phase 3: Knowledge Enhancement (Week 2)
**Priority: MEDIUM - Better knowledge management**

3. **Swap .txt → .pdf files** (1 hour)
   - Create/download real PDF documents
   - Test: Verify PDFs readable

4. **Add PDF parsing to MCP** (4 hours)
   - Install: `pip install pdfplumber pypdf2`
   - Update: `mcp_servers/knowledge/server.py`
   - Test: Verify rules extracted from PDFs

### Phase 4: Data Integration (Week 3)
**Priority: LOW - Only if connecting to real systems**

5. **Swap Mock Domain → Real DB/API** (8 hours)
   - Option A: Supabase (easier)
   - Option B: WebPT API (if available)
   - Test: Verify data loads from real source

### Phase 5: Communication (Week 4)
**Priority: LOW - Only for production**

6. **Swap Mock SMS/Email → Real** (4 hours)
   - Set up Twilio + SendGrid accounts
   - Update: `agents/patient_engagement_agent.py`
   - Test: Send real SMS/email

---

## Testing Checklist

### With Mocks (Current)
- [ ] CLI runs without errors
- [ ] Filtering eliminates P003 (location)
- [ ] Scoring ranks P001 > P004
- [ ] Consent returns "YES"
- [ ] Audit log generated
- [ ] No API calls made (free!)

### With Real LLM (After Day 4)
- [ ] LiteLLM calls succeed
- [ ] LangFuse traces visible
- [ ] Real LLM makes logical decisions
- [ ] Costs tracked in LangFuse

### With Real Knowledge (After Week 2)
- [ ] PDFs parsed correctly
- [ ] Rules extracted accurately
- [ ] Semantic search works (if using Vector DB)

### With Real Data (After Week 3)
- [ ] Database connection works
- [ ] Provider/patient data loads
- [ ] Appointments bookable

---

## Cost Tracking

| Component | Mock Cost | Real Cost (Monthly) |
|-----------|-----------|-------------------|
| LLM Calls | $0 | ~$20-50 (LiteLLM) |
| LangFuse | $0 | $0 (free tier) |
| Vector DB | $0 | ~$70 (Pinecone starter) |
| Database | $0 | ~$25 (Supabase pro) |
| SMS/Email | $0 | ~$50 (Twilio + SendGrid) |
| **Total** | **$0** | **~$165-195/month** |

**Recommendation:** Stay with mocks until architecture validated, then swap incrementally.

---

## Quick Reference Commands

```bash
# Run with all mocks (no costs)
python demo/cli.py

# Run with real LLM only
python demo/cli.py --real-llm

# Run with real LLM + LangFuse
python demo/cli.py --real-llm --real-langfuse

# Check what's mocked
grep -r "MOCK" . --include="*.py"

# View this file
cat MOCKS.md
```

---

## Notes

- **Philosophy:** Mock first, validate architecture, then swap to real services incrementally
- **Benefits:** Fast iteration, no costs during development, easy debugging
- **Trade-off:** Mocks don't catch integration issues (test with real services before production)
- **Timeline:** Mocked flow in 2-3 days, full real services in 2-3 weeks

---

Last Updated: 2024-11-15


