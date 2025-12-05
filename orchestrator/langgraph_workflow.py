"""LangGraph Workflow Orchestrator with Conditional Branching.

This implementation uses LangGraph for:
- State management across workflow stages
- Conditional routing (patient declines → try next provider)
- Error handling and retries
- Visual workflow graph

Branching scenarios:
1. Patient says NO → Offer next ranked provider
2. No candidates found → Escalate to HOD
3. All candidates declined → Manual review
"""

from typing import Dict, Any, List, Literal
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.smart_scheduling_agent import SmartSchedulingAgent
from agents.patient_engagement_agent import PatientEngagementAgent
from agents.backfill_agent import BackfillAgent
from mcp_servers.domain.json_server import create_json_domain_server


class WorkflowState(TypedDict):
    """State that flows through the LangGraph workflow."""
    # Input
    therapist_id: str
    session_id: str
    
    # Stage 1: Trigger
    appointments: List[Dict[str, Any]]
    current_appointment: Dict[str, Any]
    current_appointment_index: int
    
    # Stage 2: Filter
    candidate_provider_ids: List[str]
    qualified_provider_ids: List[str]
    
    # Stage 3: Score
    ranked_providers: List[Dict[str, Any]]
    current_provider_index: int
    current_provider_id: str
    
    # Stage 4: Consent
    patient_response: str  # "YES", "NO", "INFO", "TIMEOUT"
    consent_granted: bool
    offers_sent: int
    
    # Stage 5: Booking
    booking_result: Dict[str, Any]
    
    # Stage 6: Audit
    audit_log: Dict[str, Any]
    
    # Control flow
    status: str  # "in_progress", "success", "failed", "manual_review"
    error_message: str
    events: List[Dict[str, Any]]


class LangGraphWorkflowOrchestrator:
    """LangGraph-based workflow orchestrator with conditional branching.
    
    Workflow Graph:
    
    START → trigger → filter → score → consent
                                          ├─ [YES] → book → audit → END
                                          ├─ [NO] → next_provider → score (loop)
                                          └─ [TIMEOUT] → manual_review → END
    
    If no candidates: filter → hod_fallback → book → audit → END
    """
    
    def __init__(
        self,
        smart_scheduling_agent=None,
        patient_engagement_agent=None,
        backfill_agent=None,
        domain_server=None
    ):
        """Initialize orchestrator with agents and build workflow graph."""
        self.scheduling_agent = smart_scheduling_agent or SmartSchedulingAgent()
        self.engagement_agent = patient_engagement_agent or PatientEngagementAgent()
        self.backfill_agent = backfill_agent or BackfillAgent()
        self.domain_server = domain_server or create_json_domain_server()
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
        
        print(f"\n[ORCHESTRATOR] LangGraph Workflow Orchestrator initialized")
        print(f"[ORCHESTRATOR] Mode: State machine with conditional branching + backfill")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with conditional edges."""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes (stages)
        workflow.add_node("trigger", self._node_trigger)
        workflow.add_node("filter", self._node_filter)
        workflow.add_node("score", self._node_score)
        workflow.add_node("consent", self._node_consent)
        workflow.add_node("next_provider", self._node_next_provider)
        workflow.add_node("hod_fallback", self._node_hod_fallback)
        workflow.add_node("book", self._node_book)
        workflow.add_node("audit", self._node_audit)
        workflow.add_node("manual_review", self._node_manual_review)
        
        # Set entry point
        workflow.set_entry_point("trigger")
        
        # Add edges
        workflow.add_edge("trigger", "filter")
        
        # Conditional: After filter, check if we have candidates
        workflow.add_conditional_edges(
            "filter",
            self._route_after_filter,
            {
                "score": "score",
                "hod_fallback": "hod_fallback"
            }
        )
        
        workflow.add_edge("score", "consent")
        
        # Conditional: After consent, check patient response
        workflow.add_conditional_edges(
            "consent",
            self._route_after_consent,
            {
                "book": "book",
                "next_provider": "next_provider",
                "manual_review": "manual_review"
            }
        )
        
        # If patient declined, try next provider
        workflow.add_conditional_edges(
            "next_provider",
            self._route_after_next_provider,
            {
                "score": "score",
                "hod_fallback": "hod_fallback",
                "manual_review": "manual_review"
            }
        )
        
        # HOD fallback goes straight to booking
        workflow.add_edge("hod_fallback", "book")
        
        # After booking, create audit log
        workflow.add_edge("book", "audit")
        
        # End states
        workflow.add_edge("audit", END)
        workflow.add_edge("manual_review", END)
        
        return workflow.compile()
    
    # ========== ROUTING FUNCTIONS ==========
    
    def _route_after_filter(self, state: WorkflowState) -> Literal["score", "hod_fallback"]:
        """Route based on whether we found qualified candidates."""
        if state["qualified_provider_ids"] and len(state["qualified_provider_ids"]) > 0:
            return "score"
        else:
            print(f"[ROUTING] No qualified candidates found → HOD fallback")
            return "hod_fallback"
    
    def _route_after_consent(self, state: WorkflowState) -> Literal["book", "next_provider", "manual_review"]:
        """Route based on patient response."""
        response = state["patient_response"]
        
        if response == "YES":
            print(f"[ROUTING] Patient said YES → Book appointment")
            return "book"
        elif response == "NO":
            print(f"[ROUTING] Patient said NO → Try next provider")
            return "next_provider"
        else:  # TIMEOUT or other
            print(f"[ROUTING] Patient timeout/error → Manual review")
            return "manual_review"
    
    def _route_after_next_provider(self, state: WorkflowState) -> Literal["score", "hod_fallback", "manual_review"]:
        """Route after incrementing to next provider."""
        current_index = state["current_provider_index"]
        ranked_providers = state["ranked_providers"]
        offers_sent = state["offers_sent"]
        
        if current_index < len(ranked_providers):
            print(f"[ROUTING] Trying provider #{current_index + 1} of {len(ranked_providers)}")
            return "score"
        elif offers_sent < 3:  # Max 3 offers
            print(f"[ROUTING] All ranked providers tried → HOD fallback")
            return "hod_fallback"
        else:
            print(f"[ROUTING] Max offers reached → Manual review")
            return "manual_review"
    
    # ========== NODE FUNCTIONS ==========
    
    def _node_trigger(self, state: WorkflowState) -> WorkflowState:
        """Stage 1: Trigger - Identify affected appointments."""
        print(f"\n[STAGE 1] 🚨 Trigger - Identifying affected appointments...")
        
        therapist_id = state["therapist_id"]
        trigger_result = self.scheduling_agent.trigger_handler(therapist_id)
        
        state["appointments"] = trigger_result["appointments"]
        state["current_appointment_index"] = 0
        state["current_appointment"] = trigger_result["appointments"][0] if trigger_result["appointments"] else None
        
        state["events"].append({
            "stage": "trigger",
            "status": "success",
            "affected_count": len(trigger_result["appointments"])
        })
        
        print(f"[STAGE 1] ✅ Found {len(trigger_result['appointments'])} affected appointments")
        return state
    
    def _node_filter(self, state: WorkflowState) -> WorkflowState:
        """Stage 2: Filter - Apply compliance rules."""
        print(f"\n[STAGE 2] 🔍 Filter - Applying compliance filters...")
        
        appointment = state["current_appointment"]
        
        # Get all available provider IDs (excluding the unavailable one)
        candidate_ids = ["P001", "P003", "P004"]
        state["candidate_provider_ids"] = candidate_ids
        
        filter_result = self.scheduling_agent.filter_candidates(appointment, candidate_ids)
        
        state["qualified_provider_ids"] = filter_result["qualified_providers"]
        
        state["events"].append({
            "stage": "filter",
            "status": "success",
            "candidates": len(candidate_ids),
            "qualified": len(filter_result["qualified_providers"])
        })
        
        print(f"[STAGE 2] ✅ {len(filter_result['qualified_providers'])} providers qualified")
        return state
    
    def _node_score(self, state: WorkflowState) -> WorkflowState:
        """Stage 3: Score - Rank qualified providers."""
        print(f"\n[STAGE 3] ⭐ Score - Ranking providers...")
        
        appointment = state["current_appointment"]
        qualified_ids = state["qualified_provider_ids"]
        
        score_result = self.scheduling_agent.score_and_rank_providers(appointment, qualified_ids)
        
        state["ranked_providers"] = score_result["ranked_providers"]
        
        # If this is first scoring, set index to 0, otherwise keep current
        if "current_provider_index" not in state or state.get("offers_sent", 0) == 0:
            state["current_provider_index"] = 0
        
        if state["ranked_providers"]:
            current_index = state["current_provider_index"]
            state["current_provider_id"] = score_result["recommended_provider_id"]
            
            print(f"[STAGE 3] ✅ Offering provider #{current_index + 1}: {state['current_provider_id']}")
        
        state["events"].append({
            "stage": "score",
            "status": "success",
            "ranked_count": len(state["ranked_providers"])
        })
        
        return state
    
    def _node_consent(self, state: WorkflowState) -> WorkflowState:
        """Stage 4: Consent - Get patient approval."""
        print(f"\n[STAGE 4] 💬 Consent - Requesting patient approval...")
        
        appointment = state["current_appointment"]
        provider_id = state["current_provider_id"]
        
        consent_result = self.engagement_agent.send_offer(
            patient_id=appointment["patient_id"],
            provider_id=provider_id,
            appointment=appointment,
            original_provider_name="Dr. Sarah Johnson"
        )
        
        state["patient_response"] = consent_result["patient_response"]
        state["consent_granted"] = consent_result["consent_granted"]
        state["offers_sent"] = state.get("offers_sent", 0) + 1
        
        state["events"].append({
            "stage": "consent",
            "status": "success",
            "provider_offered": provider_id,
            "response": consent_result["patient_response"]
        })
        
        print(f"[STAGE 4] ✅ Patient response: {consent_result['patient_response']}")
        return state
    
    def _node_next_provider(self, state: WorkflowState) -> WorkflowState:
        """Move to next provider in ranked list."""
        print(f"\n[BRANCHING] ➡️ Next Provider - Patient declined, trying alternative...")
        
        state["current_provider_index"] = state.get("current_provider_index", 0) + 1
        
        ranked_providers = state["ranked_providers"]
        current_index = state["current_provider_index"]
        
        if current_index < len(ranked_providers):
            next_provider = ranked_providers[current_index]
            state["current_provider_id"] = next_provider["provider_id"]
            print(f"[BRANCHING] ✅ Next provider: {next_provider['name']} ({next_provider['provider_id']})")
        else:
            print(f"[BRANCHING] ⚠️ No more providers to try")
        
        return state
    
    def _node_hod_fallback(self, state: WorkflowState) -> WorkflowState:
        """Fallback: Assign to Head of Department."""
        print(f"\n[FALLBACK] 👨‍⚕️ HOD Assignment - No suitable providers, escalating...")
        
        # In a real system, this would assign to HOD
        # For demo, we'll use P001 as HOD fallback
        hod_provider_id = "P001"
        state["current_provider_id"] = hod_provider_id
        state["consent_granted"] = True  # HOD assignment is automatic
        
        state["events"].append({
            "stage": "hod_fallback",
            "status": "success",
            "hod_id": hod_provider_id,
            "reason": "No qualified candidates or all declined"
        })
        
        print(f"[FALLBACK] ✅ Assigned to HOD: {hod_provider_id}")
        return state
    
    def _node_book(self, state: WorkflowState) -> WorkflowState:
        """Stage 5: Book - Confirm appointment."""
        print(f"\n[STAGE 5] 📅 Book - Confirming appointment...")
        
        appointment = state["current_appointment"]
        provider_id = state["current_provider_id"]
        
        booking_data = {
            "appointment_id": appointment["appointment_id"],
            "patient_id": appointment["patient_id"],
            "provider_id": provider_id,
            "date": appointment["date"],
            "time": appointment["time"]
        }
        
        booking_result = self.domain_server.book_appointment(booking_data)
        
        if booking_result["status"] == "SUCCESS":
            self.engagement_agent.send_confirmation(
                patient_id=appointment["patient_id"],
                provider_id=provider_id,
                appointment=booking_data
            )
        
        state["booking_result"] = booking_result
        state["booking_result"]["booking_data"] = booking_data
        
        state["events"].append({
            "stage": "book",
            "status": "success",
            "confirmation": booking_result.get("confirmation_number")
        })
        
        print(f"[STAGE 5] ✅ Appointment booked: {booking_result.get('confirmation_number')}")
        return state
    
    def _node_audit(self, state: WorkflowState) -> WorkflowState:
        """Stage 6: Audit - Generate audit log."""
        print(f"\n[STAGE 6] 📊 Audit - Generating audit log...")
        
        audit_data = {
            "session_id": state["session_id"],
            "therapist_id": state["therapist_id"],
            "appointments_processed": 1,
            "appointments_rebooked": 1,
            "events": state["events"]
        }
        
        audit_result = self.scheduling_agent.create_audit_log(audit_data)
        
        state["audit_log"] = audit_result
        state["status"] = "success"
        
        print(f"[STAGE 6] ✅ Audit log complete: {audit_result.get('session_id')}")
        return state
    
    def _node_manual_review(self, state: WorkflowState) -> WorkflowState:
        """Manual review needed - patient declined all providers.
        
        Now with intelligent backfill:
        1. Add freed slot to available slots
        2. Try to backfill with high no-show risk patient from waitlist
        3. Add original patient to waitlist for rescheduling
        """
        print(f"\n[BACKFILL] 🔄 Patient declined all - initiating backfill...")
        
        appointment = state["current_appointment"]
        patient_id = appointment["patient_id"]
        
        # Step 1: Handle freed slot - try to backfill
        backfill_result = self.backfill_agent.handle_slot_freed(
            appointment=appointment,
            reason="Patient declined all providers"
        )
        
        # Step 2: Reschedule original patient
        reschedule_result = self.backfill_agent.reschedule_declined_patient(
            original_patient_id=patient_id,
            original_appointment=appointment
        )
        
        state["status"] = "backfilled" if backfill_result["status"] == "SUCCESS" else "manual_review"
        state["events"].append({
            "stage": "backfill",
            "status": backfill_result["status"],
            "backfill_result": backfill_result,
            "reschedule_result": reschedule_result,
            "reason": "Patient declined all providers - slot backfilled"
        })
        
        if backfill_result["status"] == "SUCCESS":
            print(f"[BACKFILL] ✅ Slot backfilled with {backfill_result['backfilled_with']['patient_name']}")
            print(f"[BACKFILL] 💰 Revenue preserved: {backfill_result['revenue_preserved']}")
        
        if reschedule_result["status"] == "WAITLISTED":
            print(f"[BACKFILL] 📋 Original patient added to waitlist")
        
        return state
    
    # ========== PUBLIC API ==========
    
    def process_therapist_departure(self, therapist_id: str) -> Dict[str, Any]:
        """Execute complete workflow for therapist departure using LangGraph.
        
        Args:
            therapist_id: ID of unavailable therapist
            
        Returns:
            Final workflow state with results
        """
        import uuid
        
        # Initialize state
        initial_state: WorkflowState = {
            "therapist_id": therapist_id,
            "session_id": f"SESSION-{therapist_id}-{uuid.uuid4().hex[:6]}",
            "appointments": [],
            "current_appointment": {},
            "current_appointment_index": 0,
            "candidate_provider_ids": [],
            "qualified_provider_ids": [],
            "ranked_providers": [],
            "current_provider_index": 0,
            "current_provider_id": "",
            "patient_response": "",
            "consent_granted": False,
            "offers_sent": 0,
            "booking_result": {},
            "audit_log": {},
            "status": "in_progress",
            "error_message": "",
            "events": []
        }
        
        print(f"\n{'='*70}")
        print(f"[LANGGRAPH WORKFLOW] Starting session: {initial_state['session_id']}")
        print(f"{'='*70}")
        
        # Execute workflow
        try:
            final_state = self.workflow.invoke(initial_state)
            
            print(f"\n{'='*70}")
            print(f"[WORKFLOW] ✅ Workflow complete - {final_state['status'].upper()}")
            print(f"{'='*70}")
            
            # Convert state to result format
            return {
                "final_status": final_state["status"].upper(),
                "session_id": final_state["session_id"],
                "booking_result": final_state.get("booking_result", {}),
                "events": final_state["events"]
            }
            
        except Exception as e:
            print(f"\n[WORKFLOW] ❌ Error: {str(e)}")
            return {
                "final_status": "FAILED",
                "session_id": initial_state["session_id"],
                "error": str(e),
                "events": initial_state["events"]
            }


# Convenience function
def create_langgraph_workflow_orchestrator() -> LangGraphWorkflowOrchestrator:
    """Create and return a LangGraph workflow orchestrator instance."""
    return LangGraphWorkflowOrchestrator()


if __name__ == "__main__":
    # Test the LangGraph orchestrator
    print("=== LANGGRAPH WORKFLOW ORCHESTRATOR TEST ===\n")
    
    orchestrator = create_langgraph_workflow_orchestrator()
    
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
    
    print(f"\n✅ LangGraph workflow test complete!")

