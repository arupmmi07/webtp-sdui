#!/usr/bin/env python3
"""
Test real workflow with Azure LLM and comprehensive logging
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('azure_llm_test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_full_workflow_with_logging():
    """Test the full workflow with detailed LLM logging"""
    
    print("🔥 Testing Full Workflow with Azure LLM")
    print("=" * 60)
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check Azure config
    provider = os.getenv("ORCHESTRATION_LLM_PROVIDER")
    endpoint = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
    model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-4")
    
    print(f"🔧 Configuration:")
    print(f"   Provider: {provider}")
    print(f"   Model: {model}")
    print(f"   Endpoint: {endpoint[:50] if endpoint else 'Not set'}...")
    print(f"   LangFuse: {'Enabled' if os.getenv('LANGFUSE_PUBLIC_KEY') else 'Disabled'}")
    
    try:
        # Import components
        from workflows.template_driven_orchestrator import TemplateDrivenOrchestrator
        from mcp_servers.domain.json_server import JSONDomainServer
        from agents.patient_engagement_agent import PatientEngagementAgent
        from agents.smart_scheduling_agent import SmartSchedulingAgent
        
        # Initialize components
        print("\n📋 Initializing Components...")
        domain = JSONDomainServer()
        patient_agent = PatientEngagementAgent()
        scheduling_agent = SmartSchedulingAgent()
        
        # Create orchestrator with LangFuse (Azure LLM)
        orchestrator = TemplateDrivenOrchestrator(
            domain_server=domain,
            patient_engagement_agent=patient_agent,
            booking_agent=None,  # Skip booking to focus on LLM
            smart_scheduling_agent=scheduling_agent,
            use_langfuse=True  # This should use Azure LLM
        )
        
        print("✅ Orchestrator initialized")
        
        # Test scenario: 1-day unavailability (should reschedule)
        print("\n🎯 Test Scenario: 1-day unavailability")
        print("   Provider: T001 (Sarah Johnson PT)")
        print("   Date: 2025-12-09")
        print("   Expected: Reschedule with same provider")
        
        # Add detailed logging to capture LLM calls
        print("\n🤖 Starting LLM workflow...")
        
        # Get affected appointments first
        appointments = domain.get_appointments_for_provider("T001")
        print(f"   Found {len(appointments)} appointments for T001")
        
        if appointments:
            for apt in appointments[:2]:  # Show first 2
                patient = domain.get_patient(apt['patient_id'])
                print(f"   • {apt['appointment_id']}: {patient['name']} at {apt['time']}")
        
        # Execute workflow with logging
        logger.info("=== STARTING AZURE LLM WORKFLOW ===")
        logger.info(f"Provider: T001, Date: 2025-12-09")
        
        result = orchestrator.execute_workflow(
            provider_id="T001",
            date="2025-12-09",
            reason="sick leave - testing Azure LLM"
        )
        
        logger.info("=== WORKFLOW COMPLETED ===")
        
        print("\n📊 Workflow Results:")
        print(f"   Status: {'✅ SUCCESS' if result.get('success') else '❌ FAILED'}")
        
        # Check if LLM was actually called
        if 'llm_response' in result:
            llm_response = result['llm_response']
            print(f"\n🤖 LLM Response Analysis:")
            print(f"   Type: {type(llm_response)}")
            
            if isinstance(llm_response, dict):
                assignments = llm_response.get('assignments', [])
                print(f"   Total assignments: {len(assignments)}")
                
                # Analyze each assignment
                for i, assignment in enumerate(assignments):
                    action = assignment.get('action', 'unknown')
                    provider_id = assignment.get('assigned_to', 'none')
                    reasoning = assignment.get('reasoning', 'No reasoning')
                    
                    print(f"\n   Assignment {i+1}:")
                    print(f"     Action: {action}")
                    print(f"     Provider: {provider_id}")
                    print(f"     Reasoning: {reasoning[:100]}...")
                    
                    # Check if it follows continuity logic
                    if action == "reschedule" and provider_id == "T001":
                        print(f"     ✅ CORRECT: Followed continuity rule!")
                    elif action == "assign" and provider_id != "T001":
                        print(f"     ⚠️  REASSIGNED: Check if duration > 2 days")
                    elif action == "waitlist":
                        print(f"     ℹ️  WAITLISTED: {reasoning[:50]}...")
                
                # Check summary
                summary = llm_response.get('summary', {})
                print(f"\n   Summary:")
                print(f"     Processed: {summary.get('total_processed', 0)}")
                print(f"     Rescheduled: {summary.get('rescheduled', 0)}")
                print(f"     Reassigned: {summary.get('reassigned', 0)}")
                print(f"     Waitlisted: {summary.get('waitlisted', 0)}")
                
                return True
            else:
                print(f"   ❌ Unexpected LLM response type: {type(llm_response)}")
                return False
        else:
            print("   ❌ No LLM response found - may have used fallback logic")
            return False
            
    except Exception as e:
        logger.error(f"Workflow test failed: {e}")
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_llm_logs():
    """Check if LLM calls are being logged"""
    
    print("\n" + "=" * 60)
    print("📋 Checking LLM Logs")
    
    log_file = "azure_llm_test.log"
    if os.path.exists(log_file):
        print(f"✅ Log file exists: {log_file}")
        
        with open(log_file, 'r') as f:
            logs = f.read()
        
        # Look for LLM-related log entries
        llm_keywords = [
            "LLM call", "Azure", "litellm", "completion", 
            "WORKFLOW", "prompt", "response"
        ]
        
        relevant_logs = []
        for line in logs.split('\n'):
            if any(keyword.lower() in line.lower() for keyword in llm_keywords):
                relevant_logs.append(line)
        
        if relevant_logs:
            print(f"   Found {len(relevant_logs)} LLM-related log entries:")
            for log in relevant_logs[-10:]:  # Show last 10
                print(f"   📝 {log}")
        else:
            print("   ⚠️  No LLM-related logs found")
    else:
        print(f"❌ No log file found: {log_file}")

def monitor_network_calls():
    """Show how to monitor actual network calls to Azure"""
    
    print("\n" + "=" * 60)
    print("🌐 Network Monitoring Tips")
    print("""
To verify Azure LLM calls are actually made:

1. 📊 Check Azure Portal:
   - Go to your Azure OpenAI resource
   - Check "Metrics" or "Logs" for API calls
   - Look for recent requests to your endpoint

2. 🔍 Enable LiteLLM Debug:
   Add to your test script:
   ```python
   import litellm
   litellm.set_verbose = True
   ```

3. 📝 Check Application Logs:
   - Look for "litellm" entries in logs
   - Check for HTTP requests to Azure endpoints
   - Monitor for "completion" calls

4. 🚨 Network Monitoring:
   Run: `sudo tcpdump -i any host your-azure-endpoint.com`
   (Replace with your actual Azure endpoint)

5. 📋 Environment Variables:
   Verify these are set correctly:
   - ORCHESTRATION_LLM_PROVIDER=azure
   - ORCHESTRATION_LLM_AZURE_ENDPOINT=your_endpoint
   - ORCHESTRATION_LLM_AZURE_API_KEY=your_key
""")

if __name__ == "__main__":
    print("🚀 Azure LLM Workflow Test with Logging")
    print("This will test the full workflow and verify LLM usage")
    
    # Test the workflow
    success = test_full_workflow_with_logging()
    
    # Check logs
    check_llm_logs()
    
    # Show monitoring tips
    monitor_network_calls()
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Workflow Test: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"   Log File: azure_llm_test.log")
    
    if success:
        print("\n🎉 Azure LLM is working in the full workflow!")
        print("✅ Check the logs above to verify LLM calls")
    else:
        print("\n⚠️  Check configuration and logs for issues")
        print("💡 Try the simple test first: python test_azure_simple.py")
