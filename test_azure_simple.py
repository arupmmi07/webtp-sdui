#!/usr/bin/env python3
"""
Simple Azure LLM test for demo
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

def test_azure_connection():
    """Test basic Azure LLM connection"""
    
    print("🔥 Testing Azure LLM Connection")
    print("=" * 50)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Azure config
    provider = os.getenv("ORCHESTRATION_LLM_PROVIDER")
    endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT") 
    key = os.getenv("ORCHESTRATION_LLM_AZURE_API_KEY")
    model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-4")
    
    print(f"Provider: {provider}")
    print(f"Endpoint: {endpoint[:50] if endpoint else 'Not set'}...")
    print(f"Model: {model}")
    print(f"Key: {'Set' if key else 'Not set'}")
    
    if not endpoint or not key:
        print("\n❌ Azure not configured. Set in .env:")
        print("ORCHESTRATION_LLM_PROVIDER=azure")
        print("ORCHESTRATION_LLM_AZURE_ENDPOINT=your_endpoint")
        print("ORCHESTRATION_LLM_AZURE_API_KEY=your_key")
        return False
    
    try:
        from adapters.llm.litellm_adapter import LiteLLMAdapter
        
        # Create Azure LLM adapter
        llm = LiteLLMAdapter(
            model=f"azure/{model}",
            api_base=endpoint,
            api_key=key,
            enable_langfuse=False
        )
        
        print("\n🤖 Testing Azure LLM...")
        
        # Simple test prompt
        test_prompt = """You are a healthcare scheduling assistant. 

SCENARIO: Provider Sarah Johnson PT is unavailable on 2025-12-09 (1 day).

CONTINUITY RULE: For 1-2 day unavailability, reschedule with SAME provider.

TASK: Decide what to do with this appointment:
- Patient: Maria Rodriguez
- Original Provider: Sarah Johnson PT (ID: T001)  
- Original Date: 2025-12-09
- Available slots for Sarah: 2025-12-10 at 09:00

Return JSON only:
{
  "action": "reschedule",
  "provider_id": "T001", 
  "new_date": "2025-12-10",
  "new_time": "09:00",
  "reasoning": "1-day unavailability: reschedule with same provider for continuity"
}"""

        response = llm.generate(
            prompt=test_prompt,
            system="You are a healthcare AI. Return only valid JSON.",
            max_tokens=500,
            temperature=1.0  # GPT-5 only supports temperature=1
        )
        
        print("✅ Azure LLM Response:")
        print("-" * 30)
        print(response.content)
        print("-" * 30)
        
        # Check if it's valid JSON
        import json
        try:
            result = json.loads(response.content)
            action = result.get('action')
            provider_id = result.get('provider_id')
            
            print(f"\n📋 Analysis:")
            print(f"   Action: {action}")
            print(f"   Provider: {provider_id}")
            
            if action == "reschedule" and provider_id == "T001":
                print("   ✅ CORRECT: Followed continuity rule!")
                return True
            else:
                print("   ⚠️  Unexpected response")
                return False
                
        except json.JSONDecodeError:
            print("   ❌ Invalid JSON response")
            return False
            
    except Exception as e:
        print(f"❌ Azure test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Azure LLM Simple Test")
    
    success = test_azure_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Azure LLM is working!")
        print("✅ Ready for demo with continuity logic")
    else:
        print("❌ Azure LLM test failed")
        print("Check .env configuration")
