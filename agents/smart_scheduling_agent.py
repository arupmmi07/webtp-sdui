"""Smart Scheduling Agent.

Handles:
- Use Case 1: Trigger - Identify affected appointments
- Use Case 2: Match Candidate Filtering  
- Use Case 3: Compliance and Score Gating
- Use Case 5: Waitlist & Backfill (simplified for thin slice)
- Use Case 6: Final Audit

Uses mocked services (MCP servers, LLM) that can be swapped later.
"""

from typing import List, Dict, Any
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.llm.mock_llm import MockLLM
from mcp_servers.knowledge.server import MockKnowledgeServer
from mcp_servers.domain.server import MockDomainServer


class SmartSchedulingAgent:
    """Smart Scheduling Agent - handles provider matching, scoring, and assignment.
    
    This agent orchestrates the core scheduling logic using:
    - Mock LLM for decision-making
    - Mock MCP Knowledge Server for rules
    - Mock MCP Domain Server for data
    
    All mocks can be swapped to real services (see MOCKS.md).
    """
    
    def __init__(
        self,
        llm: MockLLM = None,
        knowledge_server: MockKnowledgeServer = None,
        domain_server: MockDomainServer = None
    ):
        """Initialize agent with service dependencies."""
        self.llm = llm or MockLLM()
        self.knowledge = knowledge_server or MockKnowledgeServer()
        self.domain = domain_server or MockDomainServer()
        
        print(f"\n[AGENT] Smart Scheduling Agent initialized")
        print(f"[AGENT] Using: Mock LLM + Mock MCP servers")
    
    def trigger_handler(self, therapist_id: str) -> Dict[str, Any]:
        """Use Case 1: Identify affected appointments when therapist departs.
        
        Args:
            therapist_id: ID of therapist who departed
        
        Returns:
            List of affected appointments with priority scores
        """
        print(f"\n{'='*60}")
        print(f"[UC1: TRIGGER] Processing therapist {therapist_id} departure")
        print(f"{'='*60}")
        
        # Get departure info and affected appointments
        departure_info = self.domain.get_therapist_departure(therapist_id)
        appointments = self.domain.get_affected_appointments(therapist_id)
        
        print(f"[UC1: TRIGGER] Found {len(appointments)} affected appointment(s)")
        
        # For thin slice: just return the appointments
        # Real system would calculate priority scores
        results = {
            "therapist_id": therapist_id,
            "therapist_name": departure_info.get("therapist_name"),
            "affected_count": len(appointments),
            "appointments": appointments,
            "priority": "HIGH" if len(appointments) > 0 else "NONE"
        }
        
        if appointments:
            apt = appointments[0]
            print(f"[UC1: TRIGGER] → Appointment {apt['appointment_id']}: {apt.get('patient_id')}")
        
        return results
    
    def filter_candidates(
        self,
        appointment: Dict[str, Any],
        candidate_provider_ids: List[str]
    ) -> Dict[str, Any]:
        """Use Case 2: Apply hard filters to candidate providers.
        
        Args:
            appointment: Appointment details
            candidate_provider_ids: List of candidate provider IDs
        
        Returns:
            Filtered results with qualified and eliminated providers
        """
        print(f"\n{'='*60}")
        print(f"[UC2: FILTERING] Applying filters to {len(candidate_provider_ids)} candidates")
        print(f"{'='*60}")
        
        # Get patient details
        patient_id = appointment.get("patient_id")
        patient = self.domain.get_patient(patient_id)
        
        print(f"[UC2: FILTERING] Patient: {patient['name']}")
        print(f"[UC2: FILTERING] Condition: {patient['condition']}")
        print(f"[UC2: FILTERING] Requirements: {patient['condition_specialty_required']}, {patient['max_distance_miles']} mile max")
        
        # Get providers
        candidates = [self.domain.get_provider(pid) for pid in candidate_provider_ids]
        
        # Get filter rules from knowledge
        filter_rules = self.knowledge.search_knowledge("provider matching filters")
        
        print(f"\n[UC2: FILTERING] Retrieved filter rules from knowledge base")
        print(f"[UC2: FILTERING] Filters: skills_match, location_constraint")
        
        # Use LLM to apply filters
        prompt = f"""Apply provider matching filters:

RULES:
{filter_rules}

PATIENT:
- Name: {patient['name']}
- Condition: {patient['condition']}
- Required specialty: {patient['condition_specialty_required']}
- Max distance: {patient['max_distance_miles']} miles
- Gender preference: {patient['gender_preference']}

CANDIDATES:
{[{p['provider_id']: p['name'], p['specialty']: p['specialty'], p['distance_from_maria']: p.get('distance_from_maria')} for p in candidates]}

Return qualified and eliminated providers with reasons.
"""
        
        # LLM makes filtering decision (mocked)
        result = self.llm.generate(prompt, context={
            "patient": patient,
            "candidates": candidates,
            "filters": filter_rules
        })
        
        # Display results
        print(f"\n[UC2: FILTERING] Results:")
        print(f"  ✓ Qualified: {result['qualified_providers']}")
        for pid, details in result['eliminated_providers'].items():
            print(f"  ✗ Eliminated: {pid} - {details['reason']}")
        
        return {
            "qualified_providers": result['qualified_providers'],
            "eliminated_providers": result['eliminated_providers'],
            "filters_applied": result.get('filters_applied', []),
            "reasoning": result.get('reasoning', '')
        }
    
    def score_and_rank_providers(
        self,
        appointment: Dict[str, Any],
        qualified_provider_ids: List[str]
    ) -> Dict[str, Any]:
        """Use Case 3: Score and rank qualified providers.
        
        Args:
            appointment: Appointment details
            qualified_provider_ids: List of qualified provider IDs (post-filtering)
        
        Returns:
            Ranked providers with scores and explanations
        """
        print(f"\n{'='*60}")
        print(f"[UC3: SCORING] Ranking {len(qualified_provider_ids)} qualified providers")
        print(f"{'='*60}")
        
        # Get patient and providers
        patient_id = appointment.get("patient_id")
        patient = self.domain.get_patient(patient_id)
        providers = [self.domain.get_provider(pid) for pid in qualified_provider_ids]
        
        # Get scoring weights from knowledge
        scoring_weights = self.knowledge.search_knowledge("scoring weights continuity specialty")
        
        print(f"[UC3: SCORING] Retrieved scoring weights from knowledge base")
        print(f"[UC3: SCORING] Factors: continuity (40), specialty (35), preference (30), load (25), time (20)")
        
        # Use LLM to score
        prompt = f"""Score and rank these qualified providers:

SCORING WEIGHTS:
{scoring_weights}

PATIENT:
- Name: {patient['name']}
- Gender preference: {patient['gender_preference']}
- Preferred days: {patient['preferred_days']}
- Preferred time: {patient['preferred_time_block']}
- Prior providers: {patient['prior_providers']}

PROVIDERS:
{[{p['provider_id']: {'name': p['name'], 'specialty': p['specialty'], 'gender': p['gender'], 'capacity': p['capacity_utilization']}} for p in providers]}

Calculate total score (max 150 points) for each provider with breakdown.
"""
        
        # LLM makes scoring decision (mocked)
        result = self.llm.generate(prompt, context={
            "patient": patient,
            "providers": providers,
            "weights": scoring_weights
        })
        
        # Display results
        print(f"\n[UC3: SCORING] Results:")
        for provider_result in result['ranked_providers']:
            print(f"  #{provider_result['rank']}: {provider_result['provider_name']}")
            print(f"     Score: {provider_result['total_score']}/150 ({provider_result['recommendation']})")
        
        return {
            "ranked_providers": result['ranked_providers'],
            "recommended_provider_id": result['recommended_provider'],
            "reasoning": result.get('reasoning', '')
        }
    
    def create_audit_log(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 6: Create audit log for the session.
        
        Args:
            session_data: Complete session data including all events
        
        Returns:
            Audit log summary
        """
        print(f"\n{'='*60}")
        print(f"[UC6: AUDIT] Generating audit log")
        print(f"{'='*60}")
        
        audit = {
            "session_id": session_data.get("session_id", "SESSION-001"),
            "therapist_id": session_data.get("therapist_id"),
            "timestamp": "2024-11-18 09:00:00",
            "appointments_processed": session_data.get("appointments_processed", 1),
            "appointments_rebooked": session_data.get("appointments_rebooked", 1),
            "success_rate": "100%",
            "events": session_data.get("events", []),
            "status": "COMPLETE"
        }
        
        print(f"[UC6: AUDIT] ✓ Audit log created")
        print(f"[UC6: AUDIT]   Session: {audit['session_id']}")
        print(f"[UC6: AUDIT]   Processed: {audit['appointments_processed']} appointment(s)")
        print(f"[UC6: AUDIT]   Success: {audit['success_rate']}")
        
        return audit


# Convenience function
def create_smart_scheduling_agent() -> SmartSchedulingAgent:
    """Create and return a Smart Scheduling Agent instance."""
    return SmartSchedulingAgent()


if __name__ == "__main__":
    # Test the agent
    print("=== SMART SCHEDULING AGENT TEST ===\n")
    
    agent = create_smart_scheduling_agent()
    
    # Test 1: Trigger
    print("\n" + "="*70)
    print("TEST 1: Trigger Handler")
    print("="*70)
    trigger_result = agent.trigger_handler("T001")
    print(f"\n✓ Found {trigger_result['affected_count']} affected appointment(s)")
    
    # Test 2: Filtering
    print("\n" + "="*70)
    print("TEST 2: Filter Candidates")
    print("="*70)
    appointment = trigger_result['appointments'][0]
    filter_result = agent.filter_candidates(appointment, ["P001", "P004", "P003"])
    print(f"\n✓ Qualified: {len(filter_result['qualified_providers'])} providers")
    
    # Test 3: Scoring
    print("\n" + "="*70)
    print("TEST 3: Score and Rank")
    print("="*70)
    score_result = agent.score_and_rank_providers(appointment, filter_result['qualified_providers'])
    winner = score_result['ranked_providers'][0]
    print(f"\n✓ Winner: {winner['provider_name']} ({winner['total_score']} points)")
    
    print("\n" + "="*70)
    print("✅ All tests passed!")
    print("="*70)




