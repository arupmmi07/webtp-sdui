"""Interactive CLI Demo for Therapist Replacement System.

This CLI demonstrates the complete workflow with mocked services.

Usage:
    python demo/cli.py

Commands:
    therapist departed <ID>  - Trigger replacement workflow
    show audit              - View audit log
    show mocks              - View what's mocked
    help                    - Show help
    exit                    - Exit CLI

See MOCKS.md for what's mocked and how to swap to real services.
"""

import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator.workflow import create_workflow_orchestrator
import json


class TherapistReplacementCLI:
    """Interactive CLI for the therapist replacement system."""
    
    def __init__(self):
        self.orchestrator = None
        self.last_result = None
        self.session_history = []
        
    def start(self):
        """Start the CLI."""
        self.print_banner()
        self.print_mock_warning()
        self.print_help()
        
        # Initialize orchestrator
        print(f"\n[CLI] Initializing system...")
        self.orchestrator = create_workflow_orchestrator()
        print(f"[CLI] ✓ System ready\n")
        
        # Main loop
        while True:
            try:
                command = input("\n> ").strip()
                
                if not command:
                    continue
                
                if command.lower() in ["exit", "quit", "q"]:
                    self.exit_cli()
                    break
                
                elif command.lower() in ["help", "h", "?"]:
                    self.print_help()
                
                elif command.lower() == "show mocks":
                    self.show_mocks()
                
                elif command.lower() == "show audit":
                    self.show_audit()
                
                elif command.lower().startswith("therapist departed"):
                    parts = command.split()
                    if len(parts) >= 3:
                        therapist_id = parts[2]
                        self.process_departure(therapist_id)
                    else:
                        print("[ERROR] Usage: therapist departed <ID>")
                        print("[ERROR] Example: therapist departed T001")
                
                else:
                    print(f"[ERROR] Unknown command: {command}")
                    print("[ERROR] Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                print("\n\n[CLI] Interrupted by user")
                self.exit_cli()
                break
            except Exception as e:
                print(f"\n[ERROR] {str(e)}")
    
    def print_banner(self):
        """Print welcome banner."""
        print(f"\n{'='*70}")
        print(f"  THERAPIST REPLACEMENT SYSTEM - DEMO")
        print(f"  Mock-First Thin Slice Implementation")
        print(f"{'='*70}")
    
    def print_mock_warning(self):
        """Print mock warning."""
        print(f"\n{'⚠️ '*35}")
        print(f"  RUNNING IN MOCK MODE")
        print(f"  • No real LLM API calls (hardcoded responses)")
        print(f"  • No real SMS/Email sent (prints to console)")
        print(f"  • Using hardcoded test data")
        print(f"  • See MOCKS.md for details")
        print(f"{'⚠️ '*35}")
    
    def print_help(self):
        """Print help message."""
        print(f"\n{'─'*70}")
        print(f"AVAILABLE COMMANDS:")
        print(f"{'─'*70}")
        print(f"  therapist departed <ID>  - Start replacement workflow")
        print(f"                            Example: therapist departed T001")
        print(f"")
        print(f"  show audit              - View last workflow audit log")
        print(f"  show mocks              - List all mocked components")
        print(f"  help                    - Show this help message")
        print(f"  exit                    - Exit the CLI")
        print(f"{'─'*70}")
    
    def show_mocks(self):
        """Show what's mocked."""
        print(f"\n{'='*70}")
        print(f"MOCKED COMPONENTS")
        print(f"{'='*70}")
        print(f"""
🟡 MOCKED - Using fake/hardcoded implementation:
  
  1. LLM Calls
     • Mock: adapters/llm/mock_llm.py
     • Real: adapters/llm/litellm_adapter.py
     • Swap: Change 1 line in agent initialization
  
  2. LangFuse Prompts
     • Mock: Hardcoded strings in mock_llm.py
     • Real: Pull from LangFuse API
     • Swap: 2 hours (requires LangFuse setup)
  
  3. MCP Knowledge Server
     • Mock: Returns hardcoded rules
     • Real: Parse PDFs dynamically
     • Swap: 4 hours (add PDF parsing)
  
  4. MCP Domain Server
     • Mock: Hardcoded test data
     • Real: Connect to database/WebPT API
     • Swap: 8 hours (backend integration)
  
  5. SMS/Email
     • Mock: Print to console
     • Real: Twilio/SendGrid
     • Swap: 4 hours (API setup)

🟢 REAL - Using actual implementation:
  
  1. Workflow Orchestration (Sequential execution)
  2. Event Logging (Python list)
  3. Data Models (Pydantic/dataclasses)

{'─'*70}
See MOCKS.md for detailed swap instructions
{'─'*70}
""")
    
    def process_departure(self, therapist_id: str):
        """Process therapist departure."""
        print(f"\n{'='*70}")
        print(f"PROCESSING THERAPIST DEPARTURE: {therapist_id}")
        print(f"{'='*70}")
        
        # Run workflow
        result = self.orchestrator.process_therapist_departure(therapist_id)
        
        # Save result
        self.last_result = result
        self.session_history.append(result)
        
        # Print summary
        self.print_workflow_summary(result)
    
    def print_workflow_summary(self, result: dict):
        """Print workflow result summary."""
        print(f"\n{'='*70}")
        print(f"WORKFLOW SUMMARY")
        print(f"{'='*70}")
        
        status = result.get('final_status')
        print(f"\nStatus: {status}")
        print(f"Session ID: {result.get('session_id')}")
        
        if status == "SUCCESS":
            # Show detailed results
            trigger = result.get('trigger_result', {})
            filter_res = result.get('filter_result', {})
            score_res = result.get('score_result', {})
            consent_res = result.get('consent_result', {})
            booking = result.get('booking_result', {})
            
            print(f"\n📋 WORKFLOW STAGES:")
            print(f"  ✓ Stage 1 - Trigger: Found {trigger.get('affected_count', 0)} affected appointment(s)")
            print(f"  ✓ Stage 2 - Filtering: {len(filter_res.get('qualified_providers', []))} qualified (from 3 candidates)")
            
            if filter_res.get('eliminated_providers'):
                for pid, details in filter_res['eliminated_providers'].items():
                    print(f"      ✗ Eliminated {pid}: {details['reason']}")
            
            print(f"  ✓ Stage 3 - Scoring: Ranked {len(score_res.get('ranked_providers', []))} providers")
            if score_res.get('ranked_providers'):
                for p in score_res['ranked_providers']:
                    print(f"      #{p['rank']}: {p['provider_name']} - {p['total_score']}/150 pts ({p['recommendation']})")
            
            print(f"  ✓ Stage 4 - Consent: Patient said '{consent_res.get('patient_response')}' via {consent_res.get('channel_used', 'N/A').upper()}")
            print(f"  ✓ Stage 5 - Booking: Appointment confirmed")
            print(f"  ✓ Stage 6 - Audit: Log generated")
            
            print(f"\n📅 FINAL BOOKING:")
            print(f"  Patient: {booking.get('patient_id')}")
            print(f"  Provider: {booking.get('provider_id')}")
            print(f"  Date/Time: {booking.get('date')} at {booking.get('time')}")
            print(f"  Confirmation #: {booking.get('confirmation_number')}")
            
            print(f"\n✅ WORKFLOW COMPLETE - All stages successful!")
            
        elif status == "NO_WORK_NEEDED":
            print(f"\n📋 No affected appointments found.")
            
        elif status == "ESCALATED_TO_HOD":
            print(f"\n📋 No qualified providers found. Escalated to HOD.")
            
        elif status == "PATIENT_DECLINED":
            print(f"\n📋 Patient declined the offer. Would try next provider.")
            
        else:
            print(f"\n❌ Workflow failed or incomplete.")
        
        print(f"\n{'─'*70}")
        print(f"Type 'show audit' to see detailed audit log")
        print(f"{'─'*70}")
    
    def show_audit(self):
        """Show audit log."""
        if not self.last_result:
            print(f"\n[INFO] No workflow has been run yet.")
            print(f"[INFO] Run 'therapist departed T001' first.")
            return
        
        print(f"\n{'='*70}")
        print(f"AUDIT LOG")
        print(f"{'='*70}")
        
        audit = self.last_result.get('audit_result', {})
        
        if audit:
            print(f"\nSession ID: {audit.get('session_id')}")
            print(f"Timestamp: {audit.get('timestamp')}")
            print(f"Therapist: {audit.get('therapist_id')}")
            print(f"Appointments Processed: {audit.get('appointments_processed')}")
            print(f"Appointments Rebooked: {audit.get('appointments_rebooked')}")
            print(f"Success Rate: {audit.get('success_rate')}")
            print(f"Status: {audit.get('status')}")
        
        print(f"\n{'─'*70}")
        print(f"EVENT LOG:")
        print(f"{'─'*70}")
        
        events = self.last_result.get('events', [])
        for i, event in enumerate(events, 1):
            print(f"\n{i}. Stage: {event.get('stage', 'unknown').upper()}")
            print(f"   Status: {event.get('status', 'unknown')}")
            if event.get('error'):
                print(f"   Error: {event['error']}")
        
        print(f"\n{'─'*70}")
        print(f"Full JSON (for debugging):")
        print(f"{'─'*70}")
        print(json.dumps(self.last_result, indent=2, default=str))
    
    def exit_cli(self):
        """Exit the CLI."""
        print(f"\n{'='*70}")
        print(f"  Thank you for using the Therapist Replacement System!")
        print(f"  Sessions completed: {len(self.session_history)}")
        print(f"{'='*70}")
        print(f"\n  Next steps:")
        print(f"  • Review MOCKS.md to swap to real services")
        print(f"  • Test with your own data")
        print(f"  • Integrate with WebPT")
        print(f"\n  Goodbye! 👋\n")


def main():
    """Main entry point."""
    cli = TherapistReplacementCLI()
    cli.start()


if __name__ == "__main__":
    main()




