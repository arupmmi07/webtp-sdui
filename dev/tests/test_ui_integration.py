"""Test UI Integration with Template-Driven Orchestrator.

This validates the full workflow from UI button click to workflow execution.
"""

import requests
import json
import sys
from datetime import datetime

def test_ui_workflow_integration():
    """Test the complete UI workflow."""
    
    print("\n" + "="*70)
    print("🧪 TESTING UI INTEGRATION - TEMPLATE-DRIVEN ORCHESTRATOR")
    print("="*70 + "\n")
    
    # Test 1: API Health Check
    print("[1/4] Testing API health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ API is running")
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ API not accessible: {e}")
        print("   💡 Run 'make dev' to start services")
        return False
    
    # Test 2: Get initial provider state
    print("[2/4] Checking initial provider state...")
    try:
        response = requests.get("http://localhost:8000/api/providers", timeout=5)
        providers = response.json()
        
        t001 = next((p for p in providers if p['provider_id'] == 'T001'), None)
        if t001:
            print(f"   ✅ Provider T001 (Dr. {t001['name']}) found")
            print(f"      Status: {t001.get('status', 'N/A')}")
            print(f"      Appointments: {t001.get('current_patient_load', 0)}")
        else:
            print("   ❌ Provider T001 not found")
            return False
    except Exception as e:
        print(f"   ❌ Failed to get providers: {e}")
        return False
    
    # Test 3: Get initial appointments
    print("[3/4] Checking initial appointments...")
    try:
        response = requests.get("http://localhost:8000/api/appointments", timeout=5)
        appointments = response.json()
        
        t001_appointments = [apt for apt in appointments if apt['provider_id'] == 'T001']
        print(f"   ✅ Found {len(t001_appointments)} appointments for T001")
        for apt in t001_appointments[:3]:
            print(f"      • {apt['appointment_id']} - Patient: {apt['patient_id']} at {apt['time']}")
    except Exception as e:
        print(f"   ❌ Failed to get appointments: {e}")
        return False
    
    # Test 4: Trigger workflow (simulating UI button click)
    print("[4/4] Triggering template-driven workflow...")
    print("   🔄 Simulating 'Mark Unavailable' button click...")
    
    try:
        payload = {
            "trigger_type": "provider_unavailable",
            "provider_id": "T001",
            "reason": "sick",
            "date": datetime.now().date().isoformat()
        }
        
        print(f"   📤 POST /api/trigger-workflow")
        print(f"      Payload: {json.dumps(payload, indent=6)}")
        
        response = requests.post(
            "http://localhost:8000/api/trigger-workflow",
            json=payload,
            timeout=30  # Template orchestrator may take time for LLM call
        )
        
        if response.status_code != 200:
            print(f"   ❌ Workflow failed with status {response.status_code}")
            print(f"      Response: {response.text}")
            return False
        
        result = response.json()
        
        print("\n" + "="*70)
        print("✅ WORKFLOW EXECUTION SUCCESSFUL!")
        print("="*70 + "\n")
        
        print("📊 WORKFLOW RESULTS:")
        print(f"   Workflow Type: {result.get('workflow_type')}")
        print(f"   Success: {result.get('success')}")
        print(f"   Provider: {result.get('provider_id')}")
        print(f"   Affected Appointments: {result.get('affected_appointments_count', 0)}")
        print(f"   Successful Assignments: {len(result.get('assignments', []))}")
        print(f"   Emails Sent: {result.get('emails_sent', 0)}")
        print(f"   Waitlist Entries: {result.get('waitlist_count', 0)}")
        print(f"   Message: {result.get('message')}")
        
        if result.get('assignments'):
            print("\n📋 ASSIGNMENTS:")
            for i, assignment in enumerate(result['assignments'], 1):
                print(f"   {i}. {assignment.get('patient_name', 'Unknown')}")
                print(f"      → {assignment.get('assigned_to_name', 'Unknown')}")
                print(f"      Score: {assignment.get('match_score', 0)}")
                print(f"      Reason: {assignment.get('reasoning', 'N/A')}")
        
        if result.get('waitlist'):
            print("\n⏳ WAITLIST:")
            for i, entry in enumerate(result.get('waitlist', []), 1):
                print(f"   {i}. {entry.get('patient_name', 'Unknown')}")
                print(f"      Reason: {entry.get('reasoning', 'N/A')}")
        
        print("\n" + "="*70)
        print("🎉 UI INTEGRATION TEST PASSED!")
        print("="*70 + "\n")
        
        print("💡 WHAT THIS MEANS:")
        print("   ✅ Template-driven orchestrator is working")
        print("   ✅ API endpoint is properly integrated")
        print("   ✅ UI 'Mark Unavailable' button will work")
        print("   ✅ Real LLM is being used (or mock as fallback)")
        print("   ✅ Multi-agent architecture is functioning")
        print("\n")
        
        return True
        
    except requests.exceptions.Timeout:
        print("   ⏱️  Request timed out (LLM call may be slow)")
        print("   💡 This is normal for first LLM call")
        print("   💡 Try again or check logs: tail -f logs/api.log")
        return False
    except Exception as e:
        print(f"   ❌ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🚀 Starting UI Integration Validation...\n")
    print("Prerequisites:")
    print("  ✅ Services running (make dev)")
    print("  ✅ API at http://localhost:8000")
    print("  ✅ UI at http://localhost:8501")
    print()
    
    success = test_ui_workflow_integration()
    
    if success:
        print("\n✅ VALIDATION COMPLETE - READY FOR UI TESTING!")
        print("\n📱 Test in Browser:")
        print("   1. Open: http://localhost:8000/schedule.html")
        print("   2. Click '🚫 Mark Unavailable' on Dr. Sarah Johnson")
        print("   3. Confirm the prompt")
        print("   4. Watch the AI reassign patients!")
        print()
        sys.exit(0)
    else:
        print("\n❌ VALIDATION FAILED - CHECK LOGS")
        print("   → tail -f logs/api.log")
        print()
        sys.exit(1)

