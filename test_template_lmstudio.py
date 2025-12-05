"""Test Template-Driven Orchestrator with LM Studio.

This tests the template approach (your idea!) with a local LLM via LM Studio.
"""

import sys
import json
import requests
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from workflows.template_driven_orchestrator import create_template_driven_orchestrator
from mcp_servers.domain.json_server import JSONDomainServer
from agents.patient_engagement_agent import PatientEngagementAgent
from agents.smart_scheduling_agent import SmartSchedulingAgent
from adapters.llm.litellm_adapter import LiteLLMAdapter
from adapters.llm.mock_llm import MockLLM


# Simple BookingAgent wrapper around domain server
class BookingAgent:
    def __init__(self, domain_server):
        self.domain = domain_server
    
    def book_appointment(self, appointment_id, provider_id):
        """Book an appointment."""
        try:
            appointments = self.domain.get_appointments()
            for apt in appointments:
                if apt.get('appointment_id') == appointment_id:
                    apt['provider_id'] = provider_id
                    apt['status'] = 'rescheduled'
                    # Update in JSON
                    self.domain.update_appointment(apt)
                    return True
            return False
        except:
            return False


def check_lm_studio():
    """Check if LM Studio is running and available."""
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('data'):
                model_name = data['data'][0].get('id', 'unknown')
                return True, model_name
        return False, None
    except:
        return False, None


def test_template_with_lmstudio():
    """Test template-driven orchestrator with LM Studio."""
    
    print("\n" + "="*60)
    print("🧪 TESTING TEMPLATE-DRIVEN ORCHESTRATOR WITH LM STUDIO")
    print("="*60 + "\n")
    
    # Initialize components
    print("[1/5] Initializing domain server...")
    domain = JSONDomainServer()
    
    print("[2/5] Initializing agents...")
    patient_agent = PatientEngagementAgent(domain)
    booking_agent = BookingAgent(domain)
    scheduling_agent = SmartSchedulingAgent(domain_server=domain)
    
    print("[3/5] Configuring LLM...")
    
    # Check if LM Studio is running
    lm_studio_available, model_name = check_lm_studio()
    
    if lm_studio_available:
        print(f"   ✓ LM Studio detected (model: {model_name})")
        llm = LiteLLMAdapter(
            model=f"openai/{model_name}",  # Use detected model
            api_base="http://localhost:1234/v1",
            api_key="lm-studio",
            enable_langfuse=False
        )
        print("   ✓ Using REAL LLM via LM Studio")
    else:
        print("   ⚠️  LM Studio not running at localhost:1234")
        print("   ✓ Using MOCK LLM for testing")
        llm = MockLLM()  # Fallback to mock
        print("\n   💡 To test with real LLM:")
        print("      1. Open LM Studio")
        print("      2. Load a model")
        print("      3. Start Server (localhost:1234)")
        print("      4. Re-run this test\n")
    
    print("[4/5] Creating template-driven orchestrator...")
    orchestrator = create_template_driven_orchestrator(
        domain_server=domain,
        patient_engagement_agent=patient_agent,
        booking_agent=booking_agent,
        smart_scheduling_agent=scheduling_agent,
        llm=llm,
        use_langfuse=False  # Use local template, not LangFuse
    )
    print("   ✓ Template orchestrator created")
    
    print("[5/5] Executing workflow...")
    print("\n" + "-"*60)
    print("SCENARIO: Dr. Sarah Johnson (T001) unavailable on 2025-11-21")
    print("-"*60 + "\n")
    
    try:
        result = orchestrator.execute_workflow(
            provider_id="T001",
            date="2025-11-21",
            reason="sick"
        )
        
        # Display results
        print("\n" + "="*60)
        print("✅ WORKFLOW COMPLETE!")
        print("="*60 + "\n")
        
        print("📊 SUMMARY:")
        print(f"   Total Affected: {result.get('total_affected', 0)}")
        print(f"   Successful Assignments: {result.get('successful_assignments', 0)}")
        print(f"   Waitlist Entries: {result.get('waitlist_entries', 0)}")
        
        if result.get('assignments'):
            print("\n📋 ASSIGNMENTS:")
            for i, assignment in enumerate(result['assignments'], 1):
                print(f"   {i}. {assignment.get('patient_name', 'Unknown')}")
                print(f"      → {assignment.get('assigned_to_name', 'Unknown')}")
                print(f"      Score: {assignment.get('match_score', 0)}")
                print(f"      Reason: {assignment.get('reasoning', 'N/A')}")
                print()
        
        if result.get('waitlist'):
            print("\n⏳ WAITLIST:")
            for i, entry in enumerate(result['waitlist'], 1):
                print(f"   {i}. {entry.get('patient_name', 'Unknown')}")
                print(f"      Reason: {entry.get('reasoning', 'N/A')}")
                print()
        
        print("\n" + "="*60)
        print("🎉 TEST PASSED!")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print("\n" + "="*60)
        print("❌ TEST FAILED!")
        print("="*60)
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Is LM Studio running?")
        print("2. Is a model loaded in LM Studio?")
        print("3. Is the server started? (localhost:1234)")
        print("4. Try curl http://localhost:1234/v1/models")
        print("\n")
        return False


if __name__ == "__main__":
    success = test_template_with_lmstudio()
    sys.exit(0 if success else 1)

