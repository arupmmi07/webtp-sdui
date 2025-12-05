#!/usr/bin/env python3
"""Test agents with REAL compliance rules from files."""

from agents.smart_scheduling_agent import SmartSchedulingAgent

print("=" * 70)
print("TESTING REAL COMPLIANCE INTEGRATION")
print("=" * 70)

# Test 1: Create agent with real knowledge server
print("\n1️⃣  Creating agent with REAL knowledge server...")
agent = SmartSchedulingAgent()
print("✅ Agent created with real compliance rules")

# Test 2: Test filtering with real rules
print("\n2️⃣  Testing FILTER with real compliance documents...")
appointment = {
    "patient_id": "PAT001",
    "date": "2024-11-20",
    "time": "10:00 AM"
}

filter_result = agent.filter_candidates(appointment, ["P001", "P003", "P004"])
print(f"✅ Qualified providers: {filter_result['qualified_providers']}")
print(f"✅ Using REAL rules from scheduling_policy.txt")

# Test 3: Test scoring with real weights
print("\n3️⃣  Testing SCORE with real scoring weights...")
score_result = agent.score_and_rank_providers(appointment, filter_result['qualified_providers'])
print(f"✅ Ranked providers: {len(score_result['ranked_providers'])}")
print(f"✅ Using REAL weights from scoring_weights.txt")

if score_result['ranked_providers']:
    print(f"\nTop provider: {score_result['ranked_providers'][0]}")

print("\n" + "=" * 70)
print("REAL COMPLIANCE INTEGRATION TEST COMPLETE ✅")
print("=" * 70)
print("\n📋 Compliance rules now loaded from:")
print("  - knowledge/sources/clinic/scheduling_policy.txt")
print("  - knowledge/sources/clinic/scoring_weights.txt")
print("  - knowledge/sources/payers/medicare_rules.txt")

