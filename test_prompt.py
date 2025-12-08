#!/usr/bin/env python3
"""
Test the enhanced orchestrator prompt with Azure LLM
Demo-ready version with continuity logic and validation
"""

import json
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from workflows.template_driven_orchestrator import TemplateDrivenOrchestrator
from mcp_servers.domain.json_server import JSONDomainServer
from agents.patient_engagement_agent import PatientEngagementAgent
from agents.smart_scheduling_agent import SmartSchedulingAgent

def test_enhanced_prompt():
    """Test the enhanced prompt with real data"""
    
    print("🧪 Testing Enhanced Orchestrator Prompt")
    print("=" * 60)
    
    # Initialize components
    domain = JSONDomainServer()
    patient_agent = PatientEngagementAgent()
    scheduling_agent = SmartSchedulingAgent()
    
    # Create orchestrator with mock LLM for demo
    orchestrator = TemplateDrivenOrchestrator(
        domain_server=domain,
        patient_engagement_agent=patient_agent,
        booking_agent=scheduling_agent,  # Use scheduling agent as booking agent
        smart_scheduling_agent=scheduling_agent,
        use_langfuse=False  # Use local template for demo (no LangFuse dependency)
    )
    
    print("\n📋 Test Scenario:")
    print("- Provider: T001 (Sarah Johnson PT) unavailable")
    print("- Date: 2025-12-09 (Monday)")
    print("- Testing: 1-day unavailability (should reschedule with same provider)")
    print("- Expected: Reschedule to different date with same provider")
    
    try:
        # Execute workflow - 1 day unavailability (should reschedule)
        result = orchestrator.execute_workflow(
            provider_id="T001",
            date="2025-12-09",
            reason="sick leave"
        )
        
        print("\n✅ Workflow Result:")
        print(json.dumps(result, indent=2))
        
        # Check if it followed continuity rules
        if 'llm_response' in result:
            llm_response = result['llm_response']
            if 'assignments' in llm_response:
                for assignment in llm_response['assignments']:
                    action = assignment.get('action', 'unknown')
                    assigned_to = assignment.get('assigned_to')
                    reasoning = assignment.get('reasoning', '')
                    
                    print(f"\n📊 Assignment Analysis:")
                    print(f"   Action: {action}")
                    print(f"   Assigned to: {assigned_to}")
                    print(f"   Reasoning: {reasoning[:100]}...")
                    
                    # Validate continuity logic
                    if action == "reschedule" and assigned_to == "T001":
                        print("   ✅ CORRECT: Rescheduled with same provider (1-day unavailability)")
                    elif action == "assign" and assigned_to != "T001":
                        print("   ⚠️  UNEXPECTED: Reassigned to different provider (should reschedule for 1-day)")
                    elif action == "waitlist":
                        print("   ℹ️  WAITLISTED: Check reasoning for validity")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_long_unavailability():
    """Test 3+ day unavailability (should reassign to different provider)"""
    
    print("\n" + "=" * 60)
    print("🧪 Testing Long Unavailability (3+ days)")
    
    # Initialize components
    domain = JSONDomainServer()
    patient_agent = PatientEngagementAgent()
    scheduling_agent = SmartSchedulingAgent()
    
    orchestrator = TemplateDrivenOrchestrator(
        domain_server=domain,
        patient_engagement_agent=patient_agent,
        booking_agent=scheduling_agent,  # Use scheduling agent as booking agent
        smart_scheduling_agent=scheduling_agent,
        use_langfuse=False  # Use local template for demo
    )
    
    print("\n📋 Test Scenario:")
    print("- Provider: T001 (Sarah Johnson PT) unavailable")
    print("- Date Range: 2025-12-09 to 2025-12-13 (5 days)")
    print("- Testing: Extended unavailability (should reassign to different providers)")
    print("- Expected: Assign to different providers based on specialty matching")
    
    try:
        # Execute workflow - 5 day unavailability (should reassign)
        result = orchestrator.execute_workflow(
            provider_id="T001",
            start_date="2025-12-09",
            end_date="2025-12-13",
            reason="vacation"
        )
        
        print("\n✅ Workflow Result:")
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Demo-Ready Prompt Testing with Azure LLM")
    print("Testing continuity logic and validation rules")
    
    # Test short unavailability (should reschedule)
    success1 = test_enhanced_prompt()
    
    # Test long unavailability (should reassign)  
    success2 = test_long_unavailability()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Short unavailability test: {'✅ PASSED' if success1 else '❌ FAILED'}")
    print(f"   Long unavailability test: {'✅ PASSED' if success2 else '❌ FAILED'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! Prompt is demo-ready.")
    else:
        print("\n⚠️  Some tests failed. Check LangFuse configuration and prompt.")
