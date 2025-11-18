"""Mock MCP Knowledge Server.

This server exposes knowledge from text files via MCP protocol.
Currently MOCKED with hardcoded responses for speed.

See MOCKS.md for how to swap to real PDF parsing.
"""

import os
from pathlib import Path


class MockKnowledgeServer:
    """Mock implementation of MCP Knowledge Server.
    
    Mimics real MCP server structure but returns hardcoded knowledge
    instead of parsing files. Ready to swap with real implementation.
    """
    
    def __init__(self, knowledge_path: str = None):
        self.name = "knowledge-server"
        self.knowledge_path = knowledge_path or "knowledge/sources"
        print(f"[MOCK MCP] Knowledge Server initialized (MOCKED)")
        print(f"[MOCK MCP] Knowledge path: {self.knowledge_path}")
    
    def search_knowledge(self, query: str, source: str = "all") -> str:
        """Mock: Search knowledge files for relevant information.
        
        Args:
            query: Search query (e.g., "provider matching rules")
            source: Filter by source (clinic, payers, all)
        
        Returns:
            Relevant knowledge text (MOCKED)
        """
        print(f"[MOCK MCP] search_knowledge(query='{query}', source='{source}')")
        
        # Mock: Return hardcoded knowledge based on query keywords
        query_lower = query.lower()
        
        if "filter" in query_lower or "matching" in query_lower:
            return """
PROVIDER MATCHING RULES (from scheduling_policy.txt)

Filter 1: Skills & Certification Match
- Orthopedic cases require "Orthopedic PT" certification
- Neurological cases require "Neurological PT" certification
- General PT acceptable if 5+ years experience

Filter 2: Location Constraint
- Provider must be within patient's max distance
- Default: 10 miles from patient address
- Measurement: Driving distance

Source: clinic/scheduling_policy.txt (MOCKED)
"""
        
        elif "scoring" in query_lower or "weights" in query_lower:
            return """
PROVIDER SCORING WEIGHTS (from scoring_weights.txt)

Total: 150 points possible

Factor 1: Continuity (40 pts)
- Previously seen provider: 40 pts
- Never seen: 0 pts

Factor 2: Specialty Match (35 pts)
- Exact specialty match: 35 pts
- General PT with training: 25 pts

Factor 3: Patient Preference (30 pts)
- Gender match: 15 pts
- Location convenience: 10 pts
- Age similarity: 5 pts

Factor 4: Schedule Load Balance (25 pts)
- Formula: 25 × (1 - capacity_utilization)

Factor 5: Day/Time Match (20 pts)
- Same day AND time: 20 pts
- Same day, different time: 15 pts

Source: clinic/scoring_weights.txt (MOCKED)
"""
        
        elif "medicare" in query_lower or "poc" in query_lower:
            return """
MEDICARE POC REQUIREMENTS (from medicare_rules.txt)

Plan of Care (POC) Rules:
- POC authorization REQUIRED for all Medicare patients
- Maximum 20 visits without reauthorization
- POC must be reviewed/certified every 90 days
- Provider must be Medicare-approved (NPI registered)

POC Urgency:
- URGENT: Expires within 7 days
- WARNING: Expires within 14 days
- ROUTINE: Expires > 14 days

Source: payers/medicare_rules.txt (MOCKED)
"""
        
        else:
            return f"No knowledge found for query: {query} (MOCKED)"
    
    def get_rule(self, rule_name: str) -> dict:
        """Mock: Get specific rule by name.
        
        Args:
            rule_name: Rule identifier (e.g., "skills_match", "location_constraint")
        
        Returns:
            Rule dictionary with structure (MOCKED)
        """
        print(f"[MOCK MCP] get_rule(rule_name='{rule_name}')")
        
        # Mock: Return hardcoded rule structures
        rules = {
            "skills_match": {
                "name": "Skills & Certification Match",
                "type": "hard_filter",
                "rule": "Provider specialty must match patient condition",
                "logic": "if patient.condition_specialty_required not in provider.specialty: eliminate",
                "examples": {
                    "orthopedic": ["post-surgical knee", "hip replacement"],
                    "neurological": ["stroke recovery", "Parkinson's"],
                    "general": ["back pain", "muscle strain"]
                },
                "source": "clinic/scheduling_policy.txt (MOCKED)"
            },
            
            "location_constraint": {
                "name": "Location Constraint",
                "type": "hard_filter",
                "rule": "Provider must be within patient's max distance",
                "formula": "distance(provider.location, patient.address) <= patient.max_distance_miles",
                "default_max_distance": 10.0,
                "source": "clinic/scheduling_policy.txt (MOCKED)"
            },
            
            "continuity_scoring": {
                "name": "Continuity Score",
                "type": "scoring_factor",
                "weight": 40,
                "rule": "Has patient seen this provider before?",
                "formula": "provider.id in patient.prior_providers ? 40 : 0",
                "source": "clinic/scoring_weights.txt (MOCKED)"
            },
            
            "specialty_scoring": {
                "name": "Specialty Match Score",
                "type": "scoring_factor",
                "weight": 35,
                "rule": "How well does provider specialty match?",
                "scoring": {
                    "exact_match": 35,
                    "related": 30,
                    "general_with_cert": 25,
                    "general": 15
                },
                "source": "clinic/scoring_weights.txt (MOCKED)"
            }
        }
        
        return rules.get(rule_name, {
            "error": f"Rule '{rule_name}' not found",
            "available_rules": list(rules.keys())
        })
    
    def get_all_rules(self) -> dict:
        """Mock: Get all available rules."""
        print(f"[MOCK MCP] get_all_rules()")
        
        return {
            "filters": ["skills_match", "location_constraint"],
            "scoring_factors": ["continuity_scoring", "specialty_scoring"],
            "total_filters": 2,
            "total_scoring_factors": 2,
            "note": "This is a MOCKED subset. Real system has 8 filters + 5 scoring factors."
        }
    
    def read_file_content(self, file_path: str) -> str:
        """Read actual file content from knowledge sources.
        
        This is a REAL method (not mocked) that reads the text files we created.
        Useful for debugging or when you want to see the full documents.
        """
        full_path = Path(self.knowledge_path) / file_path
        
        if not full_path.exists():
            return f"ERROR: File not found: {full_path}"
        
        try:
            with open(full_path, 'r') as f:
                content = f.read()
            print(f"[REAL] Read {len(content)} chars from {file_path}")
            return content
        except Exception as e:
            return f"ERROR reading file: {str(e)}"


# Convenience functions for agent usage
def create_knowledge_server() -> MockKnowledgeServer:
    """Create and return a knowledge server instance."""
    return MockKnowledgeServer()


if __name__ == "__main__":
    # Test the mock server
    print("=== MOCK MCP KNOWLEDGE SERVER TEST ===\n")
    
    server = create_knowledge_server()
    
    # Test 1: Search for matching rules
    print("\n1. Testing search_knowledge (matching rules):")
    result = server.search_knowledge("provider matching filters")
    print(result[:200] + "...")
    
    # Test 2: Get specific rule
    print("\n2. Testing get_rule (skills_match):")
    rule = server.get_rule("skills_match")
    print(f"  Rule: {rule['name']}")
    print(f"  Type: {rule['type']}")
    print(f"  Source: {rule['source']}")
    
    # Test 3: Get all rules
    print("\n3. Testing get_all_rules:")
    all_rules = server.get_all_rules()
    print(f"  Filters: {all_rules['filters']}")
    print(f"  Scoring: {all_rules['scoring_factors']}")
    
    # Test 4: Read actual file
    print("\n4. Testing read_file_content (real file read):")
    content = server.read_file_content("clinic/scheduling_policy.txt")
    print(f"  Read {len(content)} characters")
    print(f"  First 100 chars: {content[:100]}...")
    
    print("\n✅ Mock Knowledge Server tests complete")




