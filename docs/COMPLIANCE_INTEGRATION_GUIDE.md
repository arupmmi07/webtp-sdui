# Compliance Documents Integration Guide

## 📋 Overview

Compliance rules are **already integrated** but currently using **hardcoded mock responses**. This guide shows you how to swap to **real compliance documents** (PDFs, YAML, Markdown).

---

## 🎯 Where Compliance Rules Are Used

### **Stage 2: Filtering** (Use Case 2)

```python
# agents/smart_scheduling_agent.py - Line 115
filter_rules = self.knowledge.search_knowledge("provider matching filters")

# Returns rules like:
# - Orthopedic cases require "Orthopedic PT" certification
# - Provider must be within patient's max distance
# - Medicare patients need Medicare-approved providers
```

**What it filters:**
- ✅ Required certifications/specializations
- ✅ License status and privileges
- ✅ Location constraints
- ✅ Capacity limits
- ✅ Insurance/payer compliance (Medicare, Workers Comp, etc.)

---

### **Stage 3: Scoring** (Use Case 3)

```python
# agents/smart_scheduling_agent.py - Line 176
scoring_weights = self.knowledge.search_knowledge("scoring weights continuity specialty")

# Returns scoring formula:
# - Continuity: 40 points
# - Specialty Match: 35 points
# - Patient Preference: 30 points
# - Schedule Load: 25 points
# - Day/Time Match: 20 points
```

**What it controls:**
- ✅ How providers are ranked
- ✅ What factors matter most
- ✅ Point values for each criterion

---

## 📁 Current File Structure

```
knowledge/
├── compliance.md               # Overview document
├── scheduling_policy.md        # Policy summary
└── sources/
    ├── clinic/
    │   ├── scheduling_policy.txt    # Filtering rules
    │   └── scoring_weights.txt      # Scoring formulas
    └── payers/
        └── medicare_rules.txt        # Medicare compliance
```

**Status:** ✅ Files exist but **not being read yet** (mocked)

---

## 🔄 Current Flow (Mocked)

```
Agent needs compliance rules
        ↓
self.knowledge.search_knowledge("provider matching filters")
        ↓
MockKnowledgeServer returns HARDCODED string
        ↓
Agent uses mocked rules
```

---

## 🚀 Real Integration (3 Options)

### **Option 1: Simple File Reader** ⭐ RECOMMENDED FOR DEMO
Read `.txt` and `.md` files directly.

**Pros:**
- ✅ Simple, no dependencies
- ✅ Fast to implement (30 minutes)
- ✅ Easy to update compliance docs

**Cons:**
- ⚠️ No PDF support (need manual conversion)
- ⚠️ Simple keyword search only

---

### **Option 2: Vector DB with Embeddings** 🚀 BEST FOR PRODUCTION
Use ChromaDB/Pinecone with OpenAI embeddings for semantic search.

**Pros:**
- ✅ Semantic search (understands meaning)
- ✅ Works with PDFs
- ✅ Handles large document sets
- ✅ Can find relevant sections automatically

**Cons:**
- ⚠️ Requires API keys (OpenAI)
- ⚠️ More complex setup

---

### **Option 3: Structured YAML** 💼 BEST FOR STRICT COMPLIANCE
Store rules in structured YAML files with validation.

**Pros:**
- ✅ Type-safe, validated rules
- ✅ Easy to audit
- ✅ No AI needed (deterministic)
- ✅ Perfect for regulatory compliance

**Cons:**
- ⚠️ Requires maintaining YAML files
- ⚠️ Less flexible than semantic search

---

## 📝 Implementation: Option 1 (Simple File Reader)

### Step 1: Create Real Knowledge Server

```python
# mcp_servers/knowledge/file_knowledge_server.py
"""Real MCP Knowledge Server - reads from actual files."""

import os
from pathlib import Path
from typing import List, Dict

class FileKnowledgeServer:
    """Real implementation that reads from .txt and .md files."""
    
    def __init__(self, knowledge_path: str = "knowledge/sources"):
        self.knowledge_path = Path(knowledge_path)
        self.cache = {}  # Cache loaded files
        print(f"[REAL MCP] Knowledge Server initialized")
        print(f"[REAL MCP] Reading from: {self.knowledge_path}")
        
        # Pre-load all knowledge files
        self._load_all_files()
    
    def _load_all_files(self):
        """Load all .txt and .md files into cache."""
        for file_path in self.knowledge_path.rglob("*.txt"):
            key = file_path.stem
            with open(file_path, 'r') as f:
                self.cache[key] = {
                    "content": f.read(),
                    "path": str(file_path),
                    "type": "clinic" if "clinic" in str(file_path) else "payer"
                }
        
        for file_path in self.knowledge_path.rglob("*.md"):
            key = file_path.stem
            with open(file_path, 'r') as f:
                self.cache[key] = {
                    "content": f.read(),
                    "path": str(file_path),
                    "type": "clinic"
                }
        
        print(f"[REAL MCP] Loaded {len(self.cache)} knowledge files")
    
    def search_knowledge(self, query: str, source: str = "all") -> str:
        """Search knowledge files for relevant information.
        
        Args:
            query: Search query (e.g., "provider matching rules")
            source: Filter by source (clinic, payers, all)
        
        Returns:
            Relevant knowledge text from files
        """
        print(f"[REAL MCP] search_knowledge(query='{query}', source='{source}')")
        
        query_lower = query.lower()
        results = []
        
        # Simple keyword matching
        if "filter" in query_lower or "matching" in query_lower:
            if "scheduling_policy" in self.cache:
                results.append(self.cache["scheduling_policy"]["content"])
        
        if "scoring" in query_lower or "weights" in query_lower:
            if "scoring_weights" in self.cache:
                results.append(self.cache["scoring_weights"]["content"])
        
        if "medicare" in query_lower:
            if "medicare_rules" in self.cache:
                results.append(self.cache["medicare_rules"]["content"])
        
        # Filter by source
        if source != "all":
            results = [r for r in results if source in str(r)]
        
        if not results:
            # Fallback: return all clinic rules
            return "\n\n".join([
                doc["content"] for doc in self.cache.values()
                if doc["type"] == "clinic"
            ])
        
        return "\n\n".join(results)
    
    def get_all_rules(self, rule_type: str = "all") -> Dict[str, str]:
        """Get all rules of a specific type.
        
        Args:
            rule_type: "filtering", "scoring", "payer", or "all"
        
        Returns:
            Dictionary of rule name to content
        """
        if rule_type == "all":
            return {k: v["content"] for k, v in self.cache.items()}
        
        return {
            k: v["content"] for k, v in self.cache.items()
            if rule_type.lower() in k.lower()
        }
    
    def reload_files(self):
        """Reload all files from disk (useful for live updates)."""
        self.cache = {}
        self._load_all_files()
        print(f"[REAL MCP] Reloaded {len(self.cache)} files")


def create_file_knowledge_server() -> FileKnowledgeServer:
    """Factory function to create file-based knowledge server."""
    return FileKnowledgeServer()
```

---

### Step 2: Update Agents to Use Real Server

```python
# agents/smart_scheduling_agent.py

# Change import
from mcp_servers.knowledge.file_knowledge_server import FileKnowledgeServer

class SmartSchedulingAgent:
    def __init__(
        self,
        llm: MockLLM = None,
        knowledge_server: FileKnowledgeServer = None,  # Changed type
        domain_server: JSONDomainServer = None
    ):
        self.llm = llm or MockLLM()
        self.knowledge = knowledge_server or FileKnowledgeServer()  # Real!
        self.domain = domain_server or create_json_domain_server()
        
        print(f"[AGENT] Using: Mock LLM + REAL Knowledge Server + JSON Domain")
```

---

### Step 3: Create Compliance Documents

**Example: `knowledge/sources/clinic/scheduling_policy.txt`**

```
PROVIDER MATCHING RULES
=======================

Last Updated: 2024-11-20
Authority: Clinical Operations Team
Compliance: HIPAA, State Regulations

FILTER 1: REQUIRED SKILLS & CERTIFICATIONS
-------------------------------------------

Orthopedic Cases:
- MUST have "Orthopedic PT" certification OR
- Board Certified Orthopedic Clinical Specialist (OCS) OR
- General PT with 5+ years orthopedic experience

Neurological Cases:
- MUST have "Neurological PT" certification OR
- Board Certified Neurologic Clinical Specialist (NCS)

Post-Surgical Cases:
- Requires orthopedic or sports medicine certification
- Must have hospital privileges if treating post-op patients

FILTER 2: LICENSE & PRIVILEGES
-------------------------------

Required:
- Active state PT license (check expiration date)
- No disciplinary actions on record
- Malpractice insurance current
- Hospital privileges if treating inpatient/post-surgical

FILTER 3: POC (Plan of Care) STATUS
------------------------------------

Medicare/Insurance Requirement:
- Provider MUST be listed on patient's active POC
- POC must not be expired
- Provider must be authorized by patient's insurance
- Check POC expiration date: Fail if < 7 days remaining

FILTER 4: PAYER RULES COMPLIANCE
---------------------------------

Medicare:
- Provider must be Medicare-approved
- Must have valid NPI number registered with Medicare
- Cannot exceed Medicare visit limits

Workers Compensation:
- Must be approved by patient's WC carrier
- Requires prior authorization for some treatments

Private Insurance:
- Check in-network status
- Verify authorization if required

FILTER 5: LOCATION CONSTRAINT
------------------------------

Standard Rule:
- Provider must be within patient's max distance preference
- Default: 10 miles from patient's home address
- Measurement: Driving distance (Google Maps API)

Exceptions:
- Specialty care: May extend to 25 miles
- Rural areas: No limit if < 3 providers within 50 miles
- Telehealth: No location constraint

FILTER 6: TELEHEALTH FLAG
--------------------------

Patient requires in-person:
- Provider must have in-person availability
- Cannot route to telehealth-only providers

Patient accepts telehealth:
- Either telehealth or in-person acceptable
- Prefer in-person for post-surgical cases

FILTER 7: AVAILABILITY CHECK
-----------------------------

Required:
- Provider must have open slot within ±3 days of original appointment
- Check calendar for conflicts
- Respect provider's blocked time

FILTER 8: CAPACITY CHECK
-------------------------

Required:
- Current patient load < max capacity
- Formula: current_load / max_capacity < 0.95 (95%)
- If at capacity, only allow if patient has relationship

ESCALATION RULES
----------------

If no providers pass all filters:
1. Relax location constraint to 25 miles
2. Accept general PT with 3+ years experience
3. Extend date range to ±7 days
4. If still none: Escalate to HOD (Head of Department)

HOD Assignment:
- Dr. Robert Williams (ID: P999)
- Always available as last resort
- Requires manual review flag

AUDIT REQUIREMENTS
------------------

Every assignment must log:
- Which filters were applied
- Why each provider was eliminated
- Final selection reasoning
- Compliance checkmarks for all rules

Source: Clinical Operations Policy Manual v3.2
Approved by: Medical Director
Effective: 2024-01-01
```

---

**Example: `knowledge/sources/clinic/scoring_weights.txt`**

```
PROVIDER SCORING WEIGHTS
========================

Last Updated: 2024-11-20
Authority: Clinical Quality Committee
Compliance: Internal QA Standards

TOTAL POSSIBLE SCORE: 150 POINTS
---------------------------------

FACTOR 1: CONTINUITY (40 points max)
-------------------------------------

Definition: Has patient seen this provider before?

Scoring:
- Previously treated by this provider: 40 points
- Treated by provider in same practice: 20 points
- Never seen: 0 points

Why Important:
- Continuity of care improves outcomes
- Patient comfort and trust
- Provider has history/context

FACTOR 2: SPECIALTY MATCH (35 points max)
-----------------------------------------

Definition: How well does provider's specialty match patient's condition?

Scoring:
- Exact specialty match (e.g., Orthopedic for knee): 35 points
- Related specialty (e.g., Sports Med for knee): 30 points
- General PT with training: 25 points
- General PT without specific training: 15 points

Examples:
- Post-surgical knee + Orthopedic PT = 35 points
- Lower back pain + General PT = 25 points
- Neurological condition + Neuro PT = 35 points

FACTOR 3: PATIENT PREFERENCE FIT (30 points max)
-----------------------------------------------

Components:
a) Gender Match (15 points)
   - Matches patient preference: 15 points
   - No preference or doesn't match: 0 points

b) Location Convenience (10 points)
   - Within 5 miles: 10 points
   - 5-10 miles: 7 points
   - 10-15 miles: 4 points
   - > 15 miles: 0 points

c) Age/Language Similarity (5 points)
   - Similar age bracket (±10 years): 3 points
   - Speaks patient's preferred language: 2 points

FACTOR 4: SCHEDULE LOAD BALANCE (25 points max)
----------------------------------------------

Definition: Distribute patients evenly, avoid overloading

Formula:
Points = 25 × (1 - capacity_utilization)

Examples:
- 40% capacity (0.40): 25 × (1 - 0.40) = 15 points
- 60% capacity (0.60): 25 × (1 - 0.60) = 10 points
- 90% capacity (0.90): 25 × (1 - 0.90) = 2.5 points

Why Important:
- Prevents provider burnout
- Maintains quality of care
- Balances workload across team

FACTOR 5: DAY/TIME MATCH (20 points max)
----------------------------------------

Components:
a) Day Match (12 points)
   - Exact day match: 12 points
   - Day within ±1 day: 8 points
   - Different day: 0 points

b) Time Block Match (8 points)
   - Exact time block (morning/afternoon): 8 points
   - Different time block: 0 points

Patient Preferences:
- Morning (7 AM - 12 PM)
- Afternoon (12 PM - 5 PM)
- Evening (5 PM - 8 PM)

SCORE INTERPRETATION
--------------------

EXCELLENT (100-150 points):
- Recommend immediately
- High confidence match
- Minimal risk

GOOD (70-99 points):
- Acceptable match
- May require patient confirmation
- Monitor for satisfaction

ACCEPTABLE (50-69 points):
- Borderline match
- Require explicit patient approval
- Document reasons

POOR (< 50 points):
- Do not recommend
- Only if HOD fallback
- Flag for manual review

TIE-BREAKING
------------

If scores within 5 points:
1. Prefer continuity (has seen patient before)
2. Prefer better specialty match
3. Prefer lower capacity utilization
4. Prefer closer location

AUDIT TRAIL
-----------

Every scoring decision must log:
- All 5 factor scores
- Total score calculated
- Tie-breaking applied (if any)
- Final ranking

Source: Clinical Quality Standards Manual v2.5
Approved by: Quality Committee
Effective: 2024-01-01
```

---

## 🎯 Testing the Integration

### Test 1: Verify Files Load

```python
# test_knowledge_integration.py
from mcp_servers.knowledge.file_knowledge_server import FileKnowledgeServer

print("Testing Knowledge Server Integration...\n")

# Create server
server = FileKnowledgeServer()

# Test 1: Search for filtering rules
print("Test 1: Filtering Rules")
rules = server.search_knowledge("provider matching filters")
print(f"Found {len(rules)} characters of rules")
print(rules[:200])  # First 200 chars

# Test 2: Search for scoring
print("\nTest 2: Scoring Weights")
weights = server.search_knowledge("scoring weights")
print(f"Found {len(weights)} characters of weights")
print(weights[:200])

# Test 3: Get all rules
print("\nTest 3: All Rules")
all_rules = server.get_all_rules()
print(f"Total rules loaded: {len(all_rules)}")
for name in all_rules.keys():
    print(f"  - {name}")

print("\n✅ Knowledge server integration working!")
```

---

### Test 2: Run Through Agent

```python
# test_agent_with_real_knowledge.py
from agents.smart_scheduling_agent import SmartSchedulingAgent
from mcp_servers.knowledge.file_knowledge_server import FileKnowledgeServer

# Create agent with REAL knowledge server
knowledge_server = FileKnowledgeServer()
agent = SmartSchedulingAgent(knowledge_server=knowledge_server)

# Test filtering
print("Testing Filter with Real Rules...\n")

appointment = {
    "patient_id": "PAT001",
    "date": "2024-11-20",
    "time": "10:00 AM"
}

result = agent.filter_candidates(appointment, ["P001", "P003", "P004"])

print(f"\nQualified: {result['qualified_providers']}")
print(f"Eliminated: {result['eliminated_providers']}")
print("\n✅ Agent using real compliance rules!")
```

---

## 📊 Option 2: Vector DB Implementation (Advanced)

For production, use semantic search with embeddings:

```python
# mcp_servers/knowledge/vector_knowledge_server.py
"""Vector DB Knowledge Server with semantic search."""

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

class VectorKnowledgeServer:
    """Knowledge server using ChromaDB for semantic search."""
    
    def __init__(self, knowledge_path: str = "knowledge/sources"):
        self.knowledge_path = Path(knowledge_path)
        
        # Initialize ChromaDB
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="compliance_rules",
            embedding_function=embedding_functions.OpenAIEmbeddingFunction(
                api_key=os.getenv("OPENAI_API_KEY")
            )
        )
        
        # Load and embed documents
        self._load_and_embed_documents()
        
        print(f"[VECTOR MCP] Knowledge Server initialized with ChromaDB")
    
    def _load_and_embed_documents(self):
        """Load all documents and create embeddings."""
        documents = []
        metadatas = []
        ids = []
        
        for file_path in self.knowledge_path.rglob("*.txt"):
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Split into chunks (for better semantic search)
                chunks = self._chunk_document(content, chunk_size=500)
                
                for i, chunk in enumerate(chunks):
                    documents.append(chunk)
                    metadatas.append({
                        "source": file_path.stem,
                        "type": "clinic" if "clinic" in str(file_path) else "payer",
                        "chunk": i
                    })
                    ids.append(f"{file_path.stem}_{i}")
        
        # Add to ChromaDB (automatically creates embeddings)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"[VECTOR MCP] Embedded {len(documents)} document chunks")
    
    def search_knowledge(self, query: str, source: str = "all", top_k: int = 3) -> str:
        """Semantic search for relevant knowledge.
        
        Args:
            query: Natural language query
            source: Filter by source type
            top_k: Number of results to return
        
        Returns:
            Relevant knowledge from top matching chunks
        """
        # Build where filter
        where = {"type": source} if source != "all" else None
        
        # Semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where
        )
        
        # Combine top results
        documents = results['documents'][0]
        return "\n\n".join(documents)
    
    def _chunk_document(self, content: str, chunk_size: int = 500) -> list:
        """Split document into chunks for better semantic search."""
        words = content.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i+chunk_size])
            chunks.append(chunk)
        
        return chunks
```

**Benefits:**
- ✅ Understands meaning, not just keywords
- ✅ "Find rules about patient gender preferences" → Finds relevant sections automatically
- ✅ Works with large document sets
- ✅ Production-ready

**Setup:**
```bash
pip install chromadb openai
export OPENAI_API_KEY=your_key_here
```

---

## 🔐 Option 3: Structured YAML (For Strict Compliance)

For regulatory environments where rules must be validated:

```yaml
# config/compliance_rules.yaml
filtering_rules:
  required_filters:
    - name: "skills_certification"
      type: "mandatory"
      rules:
        orthopedic:
          required_certifications:
            - "Orthopedic PT"
            - "OCS"
          min_experience_years_alternative: 5
        
        neurological:
          required_certifications:
            - "Neurological PT"
            - "NCS"
    
    - name: "license_privileges"
      type: "mandatory"
      rules:
        required:
          - active_license: true
          - malpractice_insurance: true
          - no_disciplinary_actions: true
    
    - name: "payer_compliance"
      type: "mandatory"
      payers:
        medicare:
          requires_npi: true
          requires_medicare_approval: true
        workers_comp:
          requires_carrier_approval: true

scoring_weights:
  total_points: 150
  factors:
    - name: "continuity"
      max_points: 40
      rules:
        previously_treated: 40
        same_practice: 20
        never_seen: 0
    
    - name: "specialty_match"
      max_points: 35
      rules:
        exact_match: 35
        related_specialty: 30
        general_with_training: 25
```

**Read with validation:**
```python
import yaml
from pydantic import BaseModel

class FilterRule(BaseModel):
    name: str
    type: str
    rules: dict

def load_compliance_rules():
    with open("config/compliance_rules.yaml") as f:
        rules = yaml.safe_load(f)
    
    # Validate structure
    for rule in rules['filtering_rules']['required_filters']:
        FilterRule(**rule)  # Pydantic validation
    
    return rules
```

---

## 🎯 Recommended Approach

### For Demo (Now):
✅ **Use Simple File Reader (Option 1)**
- Quick to implement
- Easy to show stakeholders
- Can demo with real compliance docs

### For Production (Later):
✅ **Use Vector DB (Option 2)**
- Semantic search is powerful
- Handles complex queries
- Scales to large document sets

### For Regulated Industries:
✅ **Use Structured YAML (Option 3)**
- Fully auditable
- Type-safe
- Meets compliance requirements

---

## 📝 Next Steps

1. **Choose approach** based on your needs
2. **Create compliance documents** (or use existing PDFs)
3. **Implement knowledge server**
4. **Update agent imports**
5. **Test with real rules**
6. **Demo to stakeholders!**

---

**Want me to implement Option 1 (Simple File Reader) for you now?** 

It would take ~30 minutes and you'd have real compliance rules working immediately!

