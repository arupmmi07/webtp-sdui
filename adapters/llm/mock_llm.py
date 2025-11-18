"""Mock LLM Adapter.

This adapter mimics the LiteLLM interface but returns hardcoded decisions
instead of calling a real LLM API.

Purpose: Validate architecture without API costs during development.

See MOCKS.md for how to swap to real LiteLLM + LangFuse.
"""

import json
from typing import Dict, Any, List


class MockLLM:
    """Mock LLM that mimics LiteLLMAdapter interface.
    
    Returns hardcoded, deterministic decisions for:
    - Provider filtering
    - Provider scoring
    - Patient communication
    
    Same interface as LiteLLMAdapter for easy swapping.
    """
    
    def __init__(self, model: str = "mock-model"):
        self.model = model
        self.call_count = 0
        self.total_tokens = 0
        self.cost = 0.0
        
        print(f"[MOCK LLM] Initialized (model='{model}')")
        print(f"[MOCK LLM] No API calls will be made - using hardcoded responses")
        print(f"[MOCK LLM] See MOCKS.md to swap to real LiteLLM")
    
    def generate(self, prompt: str, context: Dict[str, Any] = None, **kwargs) -> Dict[str, Any]:
        """Mock: Generate response based on prompt type.
        
        Args:
            prompt: The prompt text (analyzed for keywords)
            context: Additional context data
            **kwargs: Other parameters (ignored in mock)
        
        Returns:
            Hardcoded response matching expected structure
        """
        self.call_count += 1
        prompt_lower = prompt.lower()
        
        print(f"\n[MOCK LLM] Call #{self.call_count}")
        print(f"[MOCK LLM] Analyzing prompt: '{prompt[:80]}...'")
        
        # Detect prompt type and return appropriate mock response
        if "filter" in prompt_lower:
            return self._mock_filtering_response(context)
        
        elif "score" in prompt_lower or "rank" in prompt_lower:
            return self._mock_scoring_response(context)
        
        elif "consent" in prompt_lower or "offer" in prompt_lower:
            return self._mock_consent_response(context)
        
        else:
            return self._mock_generic_response(prompt, context)
    
    def _mock_filtering_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock filtering decision - eliminates P003 for location."""
        print(f"[MOCK LLM] Detected: FILTERING request")
        
        response = {
            "decision_type": "filtering",
            "qualified_providers": ["P001", "P004"],
            "eliminated_providers": {
                "P003": {
                    "reason": "Location constraint",
                    "details": "15 miles from patient, exceeds 10 mile limit",
                    "filter": "location_constraint"
                }
            },
            "filters_applied": [
                {
                    "filter": "skills_match",
                    "passed": ["P001", "P004", "P003"],
                    "eliminated": [],
                    "reason": "All have orthopedic qualifications"
                },
                {
                    "filter": "location_constraint",
                    "passed": ["P001", "P004"],
                    "eliminated": ["P003"],
                    "reason": "P003 at Metro PT East (15 miles) exceeds Maria's 10 mile limit"
                }
            ],
            "reasoning": """
Applied 2 filters to 3 candidate providers:

Filter 1 - Skills Match:
✓ P001 (Dr. Emily Ross): Orthopedic specialist - PASS
✓ P004 (Dr. Michael Lee): General PT with orthopedic training - PASS  
✓ P003 (Dr. Sarah Park): Orthopedic specialist - PASS

Filter 2 - Location Constraint:
✓ P001: Metro PT Main (2 miles from Maria) - PASS
✓ P004: Metro PT Main (2 miles from Maria) - PASS
✗ P003: Metro PT East (15 miles from Maria) - FAIL (exceeds 10 mile limit)

Final: 2 qualified providers (P001, P004)
""",
            "mock_note": "This is a HARDCODED response. Real LLM would analyze actual data."
        }
        
        print(f"[MOCK LLM] Returning: {len(response['qualified_providers'])} qualified")
        return response
    
    def _mock_scoring_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock scoring decision - ranks P001 > P004."""
        print(f"[MOCK LLM] Detected: SCORING request")
        
        response = {
            "decision_type": "scoring",
            "ranked_providers": [
                {
                    "provider_id": "P001",
                    "provider_name": "Dr. Emily Ross",
                    "total_score": 75,
                    "rank": 1,
                    "recommendation": "EXCELLENT",
                    "breakdown": {
                        "continuity": {"score": 0, "max": 40, "reason": "Never seen Maria before"},
                        "specialty": {"score": 35, "max": 35, "reason": "Perfect orthopedic match"},
                        "preference_fit": {"score": 30, "max": 30, "reason": "Female (matches), same clinic, similar age"},
                        "load_balance": {"score": 10, "max": 25, "reason": "60% capacity (well-balanced)"},
                        "day_time_match": {"score": 20, "max": 20, "reason": "Tuesday 10 AM - perfect match!"}
                    }
                },
                {
                    "provider_id": "P004",
                    "provider_name": "Dr. Michael Lee",
                    "total_score": 48,
                    "rank": 2,
                    "recommendation": "ACCEPTABLE",
                    "breakdown": {
                        "continuity": {"score": 40, "max": 40, "reason": "Treated Maria 2 years ago"},
                        "specialty": {"score": 25, "max": 35, "reason": "General PT with orthopedic training"},
                        "preference_fit": {"score": 5, "max": 30, "reason": "Male (doesn't match preference), same clinic"},
                        "load_balance": {"score": 3, "max": 25, "reason": "88% capacity (near max)"},
                        "day_time_match": {"score": 5, "max": 20, "reason": "Thursday PM (not preferred)"}
                    }
                }
            ],
            "recommended_provider": "P001",
            "reasoning": """
Scored 2 qualified providers using 5 factors (150 points max):

Dr. Emily Ross (P001): 75 points - EXCELLENT
+ Specialty: 35/35 (Orthopedic specialist, perfect for post-surgical knee)
+ Preference: 30/30 (Female provider, same clinic, similar age)
+ Day/Time: 20/20 (Tuesday 10 AM - Maria's exact preference!)
+ Load: 10/25 (Good availability at 60% capacity)
- Continuity: 0/40 (Never seen Maria before)

Dr. Michael Lee (P004): 48 points - ACCEPTABLE
+ Continuity: 40/40 (Treated Maria 2 years ago for same knee!)
+ Specialty: 25/35 (General PT with orthopedic training)
- Preference: 5/30 (Male, doesn't match gender preference)
- Load: 3/25 (Nearly full at 88% capacity)
- Day/Time: 5/20 (Thursday PM, not preferred)

RECOMMENDATION: Dr. Emily Ross (P001)
Despite no prior relationship, she's the best overall match with excellent
specialty qualifications and perfect alignment with Maria's preferences.
""",
            "mock_note": "This is a HARDCODED response. Real LLM would calculate actual scores."
        }
        
        print(f"[MOCK LLM] Returning: P001 ranked #1 with 75 points")
        return response
    
    def _mock_consent_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Mock consent/communication decision."""
        print(f"[MOCK LLM] Detected: CONSENT request")
        
        response = {
            "decision_type": "consent",
            "patient_response": "YES",
            "message_sent": "Hi Maria, your therapist Dr. Johnson is unavailable. We can reschedule you with Dr. Emily Ross on Tuesday 11/20 at 10:00 AM. Reply YES to confirm.",
            "channel_used": "sms",
            "response_time_minutes": 45,
            "reasoning": "Patient accepted offer (MOCKED - real system would wait for actual response)",
            "mock_note": "This is HARDCODED. Real system would send SMS via Twilio and wait for response."
        }
        
        print(f"[MOCK LLM] Returning: Patient said '{response['patient_response']}'")
        return response
    
    def _mock_generic_response(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generic mock response for unknown prompt types."""
        print(f"[MOCK LLM] Detected: GENERIC request")
        
        return {
            "decision_type": "generic",
            "response": "Mock LLM response",
            "prompt_received": prompt[:100],
            "mock_note": "This is a generic HARDCODED response."
        }
    
    def get_prompt_from_langfuse(self, prompt_name: str, **variables) -> str:
        """Mock: Get prompt from LangFuse.
        
        In real implementation, this would call LangFuse API.
        For mock, return hardcoded prompt templates.
        """
        print(f"[MOCK LLM] get_prompt_from_langfuse('{prompt_name}') - returning hardcoded")
        
        prompts = {
            "provider_filtering": """You are a medical scheduling assistant. Apply these filters to candidate providers:

Filters: {filters}

Candidate Providers: {candidates}

Patient Requirements: {patient_requirements}

Return ONLY providers that pass ALL filters. For each eliminated provider, explain why.""",
            
            "provider_scoring": """You are a medical scheduling assistant. Score these providers using the weights provided:

Scoring Weights: {weights}

Qualified Providers: {providers}

Patient Profile: {patient}

Score each provider on all factors and rank them. Show detailed breakdown.""",
            
            "patient_consent": """You are a patient communication assistant. Compose a message to get patient consent for provider change:

Original Provider: {original_provider}
New Provider: {new_provider}
Appointment: {date} at {time}

Keep message concise, friendly, and clear about what patient needs to do."""
        }
        
        template = prompts.get(prompt_name, "Default mock prompt for {prompt_name}")
        
        # Simple variable substitution if provided
        if variables:
            try:
                return template.format(**variables)
            except KeyError:
                return template
        
        return template
    
    def get_stats(self) -> Dict[str, Any]:
        """Get mock LLM usage statistics."""
        return {
            "model": self.model,
            "total_calls": self.call_count,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.cost,
            "note": "These are MOCK stats (no real API calls made)"
        }
    
    def reset_stats(self):
        """Reset usage statistics."""
        self.call_count = 0
        self.total_tokens = 0
        self.cost = 0.0


# Convenience function
def create_mock_llm() -> MockLLM:
    """Create and return a mock LLM instance."""
    return MockLLM()


if __name__ == "__main__":
    # Test the mock LLM
    print("=== MOCK LLM TEST ===\n")
    
    llm = create_mock_llm()
    
    # Test 1: Filtering
    print("\n" + "="*60)
    print("TEST 1: Provider Filtering")
    print("="*60)
    result1 = llm.generate(
        prompt="Apply these filters to candidate providers...",
        context={"candidates": ["P001", "P004", "P003"]}
    )
    print(f"\nQualified: {result1['qualified_providers']}")
    print(f"Eliminated: {list(result1['eliminated_providers'].keys())}")
    
    # Test 2: Scoring
    print("\n" + "="*60)
    print("TEST 2: Provider Scoring")
    print("="*60)
    result2 = llm.generate(
        prompt="Score and rank these qualified providers...",
        context={"providers": ["P001", "P004"]}
    )
    print(f"\nRanked:")
    for provider in result2['ranked_providers']:
        print(f"  #{provider['rank']}: {provider['provider_name']} - {provider['total_score']} pts ({provider['recommendation']})")
    
    # Test 3: Get prompt from LangFuse (mock)
    print("\n" + "="*60)
    print("TEST 3: LangFuse Prompt (mocked)")
    print("="*60)
    prompt = llm.get_prompt_from_langfuse("provider_filtering")
    print(f"\nPrompt template:\n{prompt[:150]}...")
    
    # Test 4: Stats
    print("\n" + "="*60)
    print("TEST 4: Usage Stats")
    print("="*60)
    stats = llm.get_stats()
    print(f"\nCalls made: {stats['total_calls']}")
    print(f"Model: {stats['model']}")
    print(f"Note: {stats['note']}")
    
    print("\n✅ Mock LLM tests complete")
    print("\nTo swap to real LiteLLM, change:")
    print("  from adapters.llm.mock_llm import MockLLM")
    print("  to")
    print("  from adapters.llm.litellm_adapter import LiteLLMAdapter")




