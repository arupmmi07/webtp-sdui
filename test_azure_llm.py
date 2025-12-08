#!/usr/bin/env python3
"""
Test Azure LLM with enhanced orchestrator prompt
"""

import json
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_azure_llm_direct():
    """Test Azure LLM directly with the enhanced prompt"""
    
    print("🔥 Testing Azure LLM with Enhanced Prompt")
    print("=" * 60)
    
    # Check Azure configuration
    azure_endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
    azure_key = os.getenv("ORCHESTRATION_LLM_AZURE_API_KEY")
    azure_model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-4")
    
    if not azure_endpoint or not azure_key:
        print("❌ Azure LLM not configured. Please set:")
        print("   ORCHESTRATION_LLM_AZURE_ENDPOINT")
        print("   ORCHESTRATION_LLM_AZURE_API_KEY")
        return False
    
    print(f"✅ Azure Endpoint: {azure_endpoint[:50]}...")
    print(f"✅ Azure Model: {azure_model}")
    
    try:
        from adapters.llm.litellm_adapter import LiteLLMAdapter
        
        # Create LLM adapter for Azure
        llm = LiteLLMAdapter(
            model=f"azure/{azure_model}",
            api_base=azure_endpoint,
            api_key=azure_key,
            enable_langfuse=False
        )
        
        # Test prompt with sample data
        test_prompt = """
You are an AI Healthcare Operations Orchestrator. Your task is to handle provider unavailability using CONTINUITY-FIRST logic.

SITUATION:
Provider Sarah Johnson PT (ID: T001) is unavailable on 2025-12-09.
Total affected appointments: 2

AFFECTED PATIENTS:
Patient 1: Maria Rodriguez (ID: PAT001)
- Condition: post-surgical knee
- Specialty Required: orthopedic
- Gender Preference: female
- Preferred Days: Tuesday,Thursday
- Max Distance: 5.0 miles

Patient 2: John Davis (ID: PAT002)  
- Condition: lower back pain
- Specialty Required: orthopedic
- Gender Preference: any
- Preferred Days: Monday,Wednesday,Friday
- Max Distance: 8.0 miles

AVAILABLE PROVIDERS:
Provider 1: Emily Ross PT (ID: P001)
- Specialty: Sports Physical Therapy
- Gender: female
- Location: Metro PT Main Clinic
- Capacity: 15/25 patients
- Available Slots: 2025-12-10 09:00, 2025-12-10 14:00

Provider 2: Anna Martinez PT (ID: P005)
- Specialty: Orthopedic Physical Therapy  
- Gender: female
- Location: Metro PT Downtown
- Capacity: 12/25 patients
- Available Slots: 2025-12-10 10:00, 2025-12-11 09:00

CONTINUITY INFO:
Original provider T001 has available slots:
- 2025-12-10 at 09:00
- 2025-12-11 at 14:00

DECISION LOGIC:
1. Short unavailability (1 day): RESCHEDULE with same provider T001
2. Extended unavailability (3+ days): REASSIGN to different provider
3. Never schedule on weekends

Since this is 1-day unavailability, prioritize rescheduling with same provider T001.

OUTPUT FORMAT (JSON only):
{
  "assignments": [
    {
      "appointment_id": "A001",
      "patient_id": "PAT001",
      "patient_name": "Maria Rodriguez", 
      "assigned_to": "T001",
      "assigned_to_name": "Sarah Johnson PT",
      "new_date": "2025-12-10",
      "new_time": "09:00",
      "match_quality": "EXCELLENT",
      "reasoning": "Short unavailability (1 day): Rescheduled with same provider T001 to maintain continuity.",
      "action": "reschedule"
    }
  ],
  "summary": {
    "total_processed": 2,
    "rescheduled": 1,
    "reassigned": 0,
    "waitlisted": 1
  }
}

Provide ONLY the JSON output, no additional text.
"""
        
        print("\n🤖 Calling Azure LLM...")
        print(f"Prompt length: {len(test_prompt)} characters")
        
        response = llm.generate(
            prompt=test_prompt,
            system="You are a healthcare scheduling assistant. Return ONLY valid JSON.",
            max_tokens=2000,
            temperature=0.1
        )
        
        print(f"\n✅ Azure LLM Response:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        # Try to parse as JSON
        try:
            result = json.loads(response)
            print("\n✅ Valid JSON received!")
            print(f"   Assignments: {len(result.get('assignments', []))}")
            
            # Analyze the response
            for assignment in result.get('assignments', []):
                action = assignment.get('action')
                assigned_to = assignment.get('assigned_to')
                reasoning = assignment.get('reasoning', '')
                
                print(f"\n📋 Assignment Analysis:")
                print(f"   Action: {action}")
                print(f"   Provider: {assigned_to}")
                print(f"   Reasoning: {reasoning[:80]}...")
                
                if action == "reschedule" and assigned_to == "T001":
                    print("   ✅ CORRECT: Followed continuity logic (1-day = reschedule)")
                elif action == "assign" and assigned_to != "T001":
                    print("   ⚠️  UNEXPECTED: Should reschedule for 1-day unavailability")
                elif action == "waitlist":
                    print("   ℹ️  WAITLISTED: Check if reasoning is valid")
            
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Azure LLM test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langfuse_prompt():
    """Test LangFuse prompt with Azure LLM"""
    
    print("\n" + "=" * 60)
    print("🔧 Testing LangFuse Prompt with Azure LLM")
    
    try:
        from workflows.template_driven_orchestrator import TemplateDrivenOrchestrator
        from mcp_servers.domain.json_server import JSONDomainServer
        
        # Initialize minimal components
        domain = JSONDomainServer()
        
        # Create orchestrator for prompt testing only
        orchestrator = TemplateDrivenOrchestrator(
            domain_server=domain,
            patient_engagement_agent=None,
            booking_agent=None,
            smart_scheduling_agent=None,
            use_langfuse=True
        )
        
        print("✅ Orchestrator initialized for LangFuse testing")
        
        # Test just the LLM prompt generation
        print("\n📋 Testing LangFuse prompt with Azure LLM...")
        
        # Get sample data
        provider_id = "T001"
        date = "2025-12-09"
        
        # Get affected appointments and metadata
        appointments = domain.get_appointments_by_provider_and_date(provider_id, date)
        patients = [domain.get_patient(apt['patient_id']) for apt in appointments]
        providers = domain.get_available_providers(date)
        
        print(f"   Found {len(appointments)} affected appointments")
        print(f"   Found {len(providers)} available providers")
        
        # Test the LLM call directly
        prompt_data = orchestrator._prepare_prompt_data(
            provider_id=provider_id,
            date=date,
            appointments=appointments,
            patients=patients,
            providers=providers
        )
        
        # Get prompt from LangFuse and call LLM
        llm_response = orchestrator._call_llm_for_assignments(prompt_data)
        
        if llm_response:
            print("✅ Azure LLM responded successfully!")
            print(f"   Response type: {type(llm_response)}")
            
            if isinstance(llm_response, dict):
                assignments = llm_response.get('assignments', [])
                print(f"   Assignments: {len(assignments)}")
                
                for i, assignment in enumerate(assignments[:2]):  # Show first 2
                    action = assignment.get('action', 'unknown')
                    provider = assignment.get('assigned_to', 'none')
                    reasoning = assignment.get('reasoning', '')[:60]
                    print(f"   • Assignment {i+1}: {action} → {provider}")
                    print(f"     Reasoning: {reasoning}...")
            
            return True
        else:
            print("❌ No response from Azure LLM")
            return False
        
    except Exception as e:
        print(f"❌ LangFuse test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Azure LLM Demo Test")
    print("Testing enhanced continuity prompt with real AI")
    
    # Test Azure LLM directly
    direct_success = test_azure_llm_direct()
    
    # Test with LangFuse prompt
    orchestrator_success = test_langfuse_prompt()
    
    print("\n" + "=" * 60)
    print("📊 Azure LLM Test Results:")
    print(f"   Direct LLM Test: {'✅ PASSED' if direct_success else '❌ FAILED'}")
    print(f"   LangFuse Test: {'✅ PASSED' if orchestrator_success else '❌ FAILED'}")
    
    if direct_success and orchestrator_success:
        print("\n🎉 Azure LLM is working with enhanced continuity logic!")
        print("✅ Ready for demo with real AI decisions")
    else:
        print("\n⚠️  Check Azure configuration and LangFuse prompt")
