"""Simple Workflow Orchestrator.

Orchestrates the complete therapist replacement workflow using the agents.

For thin slice: Simple sequential workflow without LangGraph complexity.
Can be enhanced with LangGraph later (see MOCKS.md).
"""

from typing import Dict, Any, List
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.smart_scheduling_agent import SmartSchedulingAgent
from agents.patient_engagement_agent import PatientEngagementAgent
from mcp_servers.domain.json_server import create_json_domain_server as create_domain_server


class SimpleWorkflowOrchestrator:
    """Simple workflow orchestrator for therapist replacement.
    
    Executes workflow stages sequentially:
    1. Trigger → Identify affected appointments
    2. Filter → Eliminate unqualified providers
    3. Score → Rank qualified providers
    4. Consent → Get patient approval
    5. Book → Confirm appointment
    6. Audit → Generate audit log
    
    For thin slice: No LangGraph, just simple sequential execution.
    Can be enhanced later with state machines and parallel processing.
    """
    
    def __init__(
        self,
        smart_scheduling_agent=None,
        patient_engagement_agent=None,
        domain_server=None
    ):
        """Initialize orchestrator with agents."""
        self.scheduling_agent = smart_scheduling_agent or SmartSchedulingAgent()
        self.engagement_agent = patient_engagement_agent or PatientEngagementAgent()
        self.domain_server = domain_server or create_domain_server()
        
        self.events = []  # Event log for audit
        
        print(f"\n[ORCHESTRATOR] Simple Workflow Orchestrator initialized")
        print(f"[ORCHESTRATOR] Mode: Sequential execution (no LangGraph)")
    
    def process_therapist_departure(self, therapist_id: str) -> Dict[str, Any]:
        """Execute complete workflow for therapist departure.
        
        Args:
            therapist_id: ID of therapist who departed
        
        Returns:
            Complete workflow result with audit log
        """
        print(f"\n{'='*70}")
        print(f"[WORKFLOW] Starting therapist replacement workflow")
        print(f"[WORKFLOW] Therapist: {therapist_id}")
        print(f"{'='*70}")
        
        session_data = {
            "session_id": f"SESSION-{therapist_id}-001",
            "therapist_id": therapist_id,
            "events": []
        }
        
        try:
            # Stage 1: Trigger
            trigger_result = self._stage_1_trigger(therapist_id)
            session_data['trigger_result'] = trigger_result
            session_data['events'].append({"stage": "trigger", "status": "complete", "data": trigger_result})
            
            if trigger_result['affected_count'] == 0:
                print(f"\n[WORKFLOW] No affected appointments. Workflow complete.")
                return self._finalize_session(session_data, status="NO_WORK_NEEDED")
            
            # For thin slice: Process only first appointment
            appointment = trigger_result['appointments'][0]
            
            # Get candidate providers (all available providers for now)
            candidate_ids = ["P001", "P004", "P003"]
            
            # Stage 2: Filtering
            filter_result = self._stage_2_filtering(appointment, candidate_ids)
            session_data['filter_result'] = filter_result
            session_data['events'].append({"stage": "filtering", "status": "complete", "data": filter_result})
            
            if len(filter_result['qualified_providers']) == 0:
                print(f"\n[WORKFLOW] No qualified providers found. Escalating to HOD.")
                return self._finalize_session(session_data, status="ESCALATED_TO_HOD")
            
            # Stage 3: Scoring
            score_result = self._stage_3_scoring(appointment, filter_result['qualified_providers'])
            session_data['score_result'] = score_result
            session_data['events'].append({"stage": "scoring", "status": "complete", "data": score_result})
            
            top_provider_id = score_result['recommended_provider_id']
            
            # Stage 4: Consent
            consent_result = self._stage_4_consent(appointment, top_provider_id)
            session_data['consent_result'] = consent_result
            session_data['events'].append({"stage": "consent", "status": "complete", "data": consent_result})
            
            if not consent_result['consent_granted']:
                print(f"\n[WORKFLOW] Patient declined. Would try next provider or escalate.")
                return self._finalize_session(session_data, status="PATIENT_DECLINED")
            
            # Stage 5: Book
            booking_result = self._stage_5_booking(appointment, top_provider_id)
            session_data['booking_result'] = booking_result
            session_data['events'].append({"stage": "booking", "status": "complete", "data": booking_result})
            
            # Stage 6: Audit
            audit_result = self._stage_6_audit(session_data)
            session_data['audit_result'] = audit_result
            
            print(f"\n{'='*70}")
            print(f"[WORKFLOW] ✅ Workflow complete - SUCCESS")
            print(f"{'='*70}")
            
            return self._finalize_session(session_data, status="SUCCESS")
            
        except Exception as e:
            print(f"\n[WORKFLOW] ❌ Error: {str(e)}")
            session_data['events'].append({"stage": "error", "error": str(e)})
            return self._finalize_session(session_data, status="ERROR")
    
    def _stage_1_trigger(self, therapist_id: str) -> Dict[str, Any]:
        """Stage 1: Identify affected appointments."""
        print(f"\n[STAGE 1] Trigger: Identifying affected appointments...")
        return self.scheduling_agent.trigger_handler(therapist_id)
    
    def _stage_2_filtering(self, appointment: Dict[str, Any], candidate_ids: List[str]) -> Dict[str, Any]:
        """Stage 2: Filter candidates."""
        print(f"\n[STAGE 2] Filtering: Applying hard filters...")
        return self.scheduling_agent.filter_candidates(appointment, candidate_ids)
    
    def _stage_3_scoring(self, appointment: Dict[str, Any], qualified_ids: List[str]) -> Dict[str, Any]:
        """Stage 3: Score and rank."""
        print(f"\n[STAGE 3] Scoring: Ranking qualified providers...")
        return self.scheduling_agent.score_and_rank_providers(appointment, qualified_ids)
    
    def _stage_4_consent(self, appointment: Dict[str, Any], provider_id: str) -> Dict[str, Any]:
        """Stage 4: Get patient consent."""
        print(f"\n[STAGE 4] Consent: Requesting patient approval...")
        return self.engagement_agent.send_offer(
            patient_id=appointment['patient_id'],
            provider_id=provider_id,
            appointment=appointment,
            original_provider_name=appointment.get('original_provider_name', 'your therapist')
        )
    
    def _stage_5_booking(self, appointment: Dict[str, Any], provider_id: str) -> Dict[str, Any]:
        """Stage 5: Book appointment."""
        print(f"\n[STAGE 5] Booking: Confirming appointment...")
        
        booking_data = {
            "appointment_id": appointment['appointment_id'],
            "patient_id": appointment['patient_id'],
            "provider_id": provider_id,
            "date": appointment['date'],
            "time": appointment['time']
        }
        
        book_result = self.domain_server.book_appointment(booking_data)
        
        # Send confirmation to patient
        if book_result['status'] == "SUCCESS":
            confirm_result = self.engagement_agent.send_confirmation(
                patient_id=appointment['patient_id'],
                provider_id=provider_id,
                appointment=booking_data
            )
            book_result['confirmation_sent'] = confirm_result['confirmation_sent']
        
        # Include booking data for reference
        book_result['booking_data'] = booking_data
        
        return book_result
    
    def _stage_6_audit(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 6: Generate audit log."""
        print(f"\n[STAGE 6] Audit: Generating audit log...")
        
        session_data['appointments_processed'] = 1
        session_data['appointments_rebooked'] = 1
        
        return self.scheduling_agent.create_audit_log(session_data)
    
    def _finalize_session(self, session_data: Dict[str, Any], status: str) -> Dict[str, Any]:
        """Finalize workflow session."""
        session_data['final_status'] = status
        return session_data


# Convenience function
def create_workflow_orchestrator() -> SimpleWorkflowOrchestrator:
    """Create and return a workflow orchestrator instance."""
    return SimpleWorkflowOrchestrator()


if __name__ == "__main__":
    # Test the orchestrator
    print("=== WORKFLOW ORCHESTRATOR TEST ===\n")
    
    orchestrator = create_workflow_orchestrator()
    
    # Run complete workflow
    result = orchestrator.process_therapist_departure("T001")
    
    print(f"\n{'='*70}")
    print(f"WORKFLOW RESULT:")
    print(f"{'='*70}")
    print(f"Status: {result['final_status']}")
    print(f"Session: {result['session_id']}")
    print(f"Stages completed: {len(result['events'])}")
    
    if result['final_status'] == "SUCCESS":
        booking = result['booking_result']
        booking_data = booking.get('booking_data', {})
        print(f"\nFinal Booking:")
        print(f"  Patient: {booking_data.get('patient_id', 'N/A')}")
        print(f"  Provider: {booking_data.get('provider_id', 'N/A')}")
        print(f"  Date/Time: {booking_data.get('date', 'N/A')} at {booking_data.get('time', 'N/A')}")
        print(f"  Confirmation: {booking.get('confirmation_number', 'N/A')}")
    
    print(f"\n✅ Workflow test complete!")




