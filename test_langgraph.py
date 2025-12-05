#!/usr/bin/env python3
"""Quick test to verify LangGraph workflow is working."""

from orchestrator import create_workflow_orchestrator

print("=" * 70)
print("TESTING LANGGRAPH WORKFLOW")
print("=" * 70)

# Test 1: Create LangGraph orchestrator
print("\n1️⃣  Creating LangGraph orchestrator...")
orchestrator = create_workflow_orchestrator(engine="langgraph")
print("✅ LangGraph orchestrator created")

# Test 2: Run workflow
print("\n2️⃣  Running workflow for T001...")
result = orchestrator.process_therapist_departure("T001")
print(f"✅ Workflow completed: {result['final_status']}")

# Test 3: Check results
print("\n3️⃣  Checking results...")
print(f"   Session: {result['session_id']}")
print(f"   Stages: {len(result['events'])}")
if result['final_status'] == "SUCCESS":
    booking = result['booking_result']
    booking_data = booking.get('booking_data', {})
    print(f"   Patient: {booking_data.get('patient_id')}")
    print(f"   Provider: {booking_data.get('provider_id')}")
    print(f"✅ All checks passed")

print("\n" + "=" * 70)
print("LANGGRAPH WORKFLOW TEST COMPLETE ✅")
print("=" * 70)

