#!/usr/bin/env python3
"""
Test ONLY the Azure LLM call in the orchestrator
"""

import os
import sys
import json
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_azure_llm_in_orchestrator():
    """Test just the LLM call part of the orchestrator"""
    
    print("🔥 Testing Azure LLM in Orchestrator (LLM Call Only)")
    print("=" * 60)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check config
    provider = os.getenv("ORCHESTRATION_LLM_PROVIDER")
    model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-4")
    endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
    
    print(f"🔧 Configuration:")
    print(f"   Provider: {provider}")
    print(f"   Model: {model}")
    print(f"   Endpoint: {endpoint[:50] if endpoint else 'Not set'}...")
    
    try:
        # Import components
        from workflows.template_driven_orchestrator import TemplateDrivenOrchestrator
        from mcp_servers.domain.json_server import JSONDomainServer
        
        # Initialize minimal components
        domain = JSONDomainServer()
        
        # Create orchestrator (no booking agent to avoid errors)
        orchestrator = TemplateDrivenOrchestrator(
            domain_server=domain,
            patient_engagement_agent=None,
            booking_agent=None,  # Skip booking to focus on LLM
            smart_scheduling_agent=None,
            use_langfuse=True
        )
        
        print("✅ Orchestrator initialized")
        
        # Test just the metadata preparation and LLM call
        print("\n📋 Preparing test data...")
        
        provider_id = "T001"
        date = "2025-12-09"
        
        # Prepare metadata (this should work)
        metadata = orchestrator.prepare_metadata(provider_id, date, date)
        print(f"   ✅ Metadata prepared: {len(metadata.get('appointments', []))} appointments")
        
        # Get prompt from LangFuse
        prompt = orchestrator.get_prompt_with_variables(metadata)
        print(f"   ✅ Prompt compiled: {len(prompt)} characters")
        
        # Test the LLM call directly
        print(f"\n🤖 Testing Azure LLM call...")
        print(f"   Model: {orchestrator.llm.model}")
        print(f"   API Base: {orchestrator.llm.api_base}")
        
        # Make the LLM call
        response = orchestrator.llm.generate(
            prompt=prompt,
            system="You are a healthcare scheduling assistant. Return ONLY valid JSON.",
            max_tokens=8000,  # Fixed token limit
            temperature=1.0   # GPT-5 requirement
        )
        
        print(f"\n✅ Azure LLM Response Received!")
        print(f"   Response length: {len(response.content)} characters")
        print(f"   Usage: {response.usage}")
        
        # Try to parse the JSON
        try:
            result = json.loads(response.content)
            assignments = result.get('assignments', [])
            
            print(f"\n📊 LLM Response Analysis:")
            print(f"   Valid JSON: ✅")
            print(f"   Assignments: {len(assignments)}")
            
            # Analyze first assignment
            if assignments:
                first = assignments[0]
                action = first.get('action', 'unknown')
                provider_id = first.get('assigned_to', 'none')
                reasoning = first.get('reasoning', 'No reasoning')[:100]
                
                print(f"\n   First Assignment:")
                print(f"     Action: {action}")
                print(f"     Provider: {provider_id}")
                print(f"     Reasoning: {reasoning}...")
                
                # Check continuity logic
                if action == "reschedule" and provider_id == "T001":
                    print(f"     ✅ CORRECT: Followed continuity rule!")
                    return True
                elif action == "assign":
                    print(f"     ℹ️  REASSIGNED: Check if this is correct")
                    return True
                elif action == "waitlist":
                    print(f"     ℹ️  WAITLISTED: Check reasoning")
                    return True
                else:
                    print(f"     ⚠️  UNEXPECTED: {action} → {provider_id}")
                    return False
            else:
                print(f"   ❌ No assignments in response")
                return False
                
        except json.JSONDecodeError as e:
            print(f"   ❌ Invalid JSON: {e}")
            print(f"   Raw response: {response.content[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Azure LLM Only Test")
    print("Testing just the LLM call without booking logic")
    
    success = test_azure_llm_in_orchestrator()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Azure LLM is working perfectly!")
        print("✅ LangFuse prompt + Azure GPT-5 = Success")
        print("✅ Ready for demo!")
    else:
        print("❌ Azure LLM test failed")
        print("Check the response above for details")
