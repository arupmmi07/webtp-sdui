"""Smart Scheduling Agent.

Handles:
- Use Case 1: Trigger - Identify affected appointments
- Use Case 2: Match Candidate Filtering  
- Use Case 3: Compliance and Score Gating
- Use Case 5: Waitlist & Backfill (simplified for thin slice)
- Use Case 6: Final Audit

Uses real LLM by default (LM Studio or cloud API), with mock as fallback.
"""

from typing import List, Dict, Any
import sys
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from adapters.llm.base import BaseLLM
from adapters.llm.mock_llm import MockLLM
from mcp_servers.knowledge.file_knowledge_server import FileKnowledgeServer, create_file_knowledge_server
from mcp_servers.domain.json_server import JSONDomainServer, create_json_domain_server


# Import LiteLLM adapter if available
try:
    from adapters.llm.litellm_adapter import LiteLLMAdapter
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class SmartSchedulingAgent:
    """Smart Scheduling Agent - handles provider matching, scoring, and assignment.
    
    This agent orchestrates the core scheduling logic using:
    - Real LLM (LiteLLM) by default - connects to LM Studio or cloud APIs
    - Mock LLM as fallback (if USE_MOCK_LLM=true)
    - File-based Knowledge Server (REAL compliance rules!)
    - JSON Domain Server (REAL data from JSON files!)
    """
    
    def __init__(
        self,
        llm: BaseLLM = None,
        knowledge_server: FileKnowledgeServer = None,
        domain_server: JSONDomainServer = None
    ):
        """Initialize agent with service dependencies."""
        # Determine which LLM to use
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if llm:
            # Use provided LLM
            self.llm = llm
            llm_type = "Custom LLM"
        elif use_mock or not LITELLM_AVAILABLE:
            # Use Mock LLM
            self.llm = MockLLM()
            llm_type = "Mock LLM"
            if not use_mock:
                print(f"[AGENT] Warning: LiteLLM not available, using Mock LLM")
        else:
            # Use Real LLM via LiteLLM (LM Studio by default)
            # Defaults to LM Studio at localhost:1234 - can override with env vars
            litellm_base_url = os.getenv("LITELLM_BASE_URL", "http://localhost:1234/v1")
            litellm_api_key = os.getenv("LITELLM_API_KEY", "lm-studio")
            default_model = os.getenv("LITELLM_DEFAULT_MODEL", "openai/gpt-oss-20b")
            
            # Try to use LiteLLM
            if litellm_base_url and litellm_api_key and default_model:
                try:
                    self.llm = LiteLLMAdapter(
                        model=default_model,
                        api_base=litellm_base_url,
                        api_key=litellm_api_key,
                        enable_langfuse=False
                    )
                    llm_type = f"Real LLM ({default_model})"
                except Exception as e:
                    print(f"[AGENT] Warning: LiteLLM configuration failed - {e}")
                    print(f"[AGENT] Falling back to Mock LLM")
                    self.llm = MockLLM()
                    llm_type = "Mock LLM (LiteLLM config failed)"
            else:
                # No LiteLLM config - use Mock for fast, deterministic demo
                print(f"[AGENT] No LiteLLM config found (set LITELLM_BASE_URL, LITELLM_API_KEY, LITELLM_DEFAULT_MODEL)")
                print(f"[AGENT] Using Mock LLM for demo")
                self.llm = MockLLM()
                llm_type = "Mock LLM (No LiteLLM config)"
        
        self.knowledge = knowledge_server or create_file_knowledge_server()
        self.domain = domain_server or create_json_domain_server()
        
        print(f"\n[AGENT] Smart Scheduling Agent initialized")
        print(f"[AGENT] LLM: {llm_type}")
        print(f"[AGENT] Knowledge: File-based (real compliance rules)")
        print(f"[AGENT] Domain: JSON-based (real data)")
    
    def trigger_handler(self, therapist_id: str) -> Dict[str, Any]:
        """
        UC1: Identify affected appointments when therapist departs.
        
        Args:
            therapist_id: ID of departing therapist
            
        Returns:
            Dict with affected appointments and therapist info
        """
        print(f"\n{'='*60}")
        print(f"[UC1: TRIGGER] Processing therapist {therapist_id} departure")
        print(f"{'='*60}")
        
        # Get therapist info
        print(f"[JSON] get_therapist_departure(therapist_id='{therapist_id}')")
        therapist = self.domain.get_provider(therapist_id)
        
        if not therapist:
            print(f"[UC1: TRIGGER] ❌ Therapist {therapist_id} not found")
            return {
                "therapist_id": therapist_id,
                "therapist": None,
                "affected_appointments": []
            }
        
        print(f"[JSON] get_provider(provider_id='{therapist_id}')")
        print(f"[JSON] get_affected_appointments(therapist_id='{therapist_id}')")
        
        # Get affected appointments
        appointments = self.domain.get_affected_appointments(therapist_id)
        
        print(f"📋 Found {len(appointments)} scheduled appointments for {therapist_id}")
        
        for apt in appointments:
            print(f"   - {apt.get('appointment_id')}: {apt.get('patient_id')} on {apt.get('date')} at {apt.get('time')}")
        
        print(f"[UC1: TRIGGER] Found {len(appointments)} affected appointment(s)")
        
        return {
            "therapist_id": therapist_id,
            "therapist_name": therapist.get("name", "Unknown") if therapist else "Unknown",
            "therapist": therapist,
            "affected_count": len(appointments),
            "appointments": appointments,
            "affected_appointments": appointments,  # Keep for backwards compatibility
            "priority": "HIGH" if len(appointments) > 0 else "NONE"
        }
    
    def filter_candidates(
        self,
        patient_id: str,
        appointment_id: str,
        candidate_ids: List[str]
    ) -> List[str]:
        """
        UC2: Filter candidate providers based on compliance rules.
        
        Uses LLM to apply filtering rules from knowledge base.
        
        Args:
            patient_id: Patient ID
            appointment_id: Appointment ID
            candidate_ids: List of candidate provider IDs
            
        Returns:
            List of qualified provider IDs
        """
        print(f"\n{'='*60}")
        print(f"[UC2: FILTERING] Applying filters to {len(candidate_ids)} candidates")
        print(f"{'='*60}")
        
        # Get patient and appointment details
        patient = self.domain.get_patient(patient_id)
        appointment = next((a for a in self.domain.get_affected_appointments("ALL") 
                           if a.get("appointment_id") == appointment_id), None)
        
        # Get candidate provider details
        candidates = [self.domain.get_provider(pid) for pid in candidate_ids]
        
        # Get filtering rules from knowledge base
        print(f"[REAL MCP] search_knowledge(query='provider matching filters', source='all')")
        filter_rules = self.knowledge.search_knowledge(
            query="provider matching filters",
            source="all"
        )
        
        # Use LLM to apply filters
        if isinstance(self.llm, MockLLM):
            # Mock mode - simple filtering logic
            # Filter by specialty match
            qualified = [c.get('provider_id') for c in candidates 
                        if c.get('specialty') == patient.get('condition_specialty_required') 
                        and c.get('status') == 'active']
            print(f"  [Mock] Simple filtering: {len(qualified)} qualified")
        else:
            # Real LLM mode - use AI reasoning
            prompt = f"""You are a healthcare scheduling assistant. Apply these filtering rules to find qualified providers.

FILTERING RULES:
{filter_rules}

PATIENT:
{patient}

APPOINTMENT:
{appointment}

CANDIDATES:
{candidates}

Return only the provider IDs that pass ALL filters, as a JSON array like ["P001", "P002"].
"""
            response = self.llm.generate(
                prompt=prompt,
                system="You are a healthcare scheduling assistant. Be concise and return only valid JSON.",
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse response
            import json
            try:
                qualified = json.loads(response.content.strip())
            except:
                # Fallback if JSON parsing fails
                print(f"[AGENT] Warning: Failed to parse LLM response, using all candidates")
                qualified = candidate_ids
        
        print(f"  ✓ Qualified: {qualified}")
        print(f"[UC2: FILTERING] {len(qualified)} provider(s) passed filters")
        
        # Return structured result for UI
        return {
            "qualified_providers": qualified,
            "eliminated_providers": {pid: {"reason": "Did not meet all filters"} 
                                    for pid in candidate_ids if pid not in qualified},
            "filters_applied": [
                {
                    "filter": "Specialty & Status",
                    "passed": qualified,
                    "eliminated": [pid for pid in candidate_ids if pid not in qualified],
                    "reason": "Must match specialty and be active"
                }
            ]
        }
    
    def calculate_match_score(
        self,
        patient_id: str,
        provider_id: str,
        original_provider_id: str = None,
        appointment_id: str = None
    ) -> Dict[str, Any]:
        """
        Calculate match score for a single patient-provider pair.
        
        Used by template orchestrator to pre-calculate all scores.
        
        Args:
            patient_id: Patient ID
            provider_id: Candidate provider ID
            original_provider_id: Original provider ID (for comparison)
            appointment_id: Appointment ID (to get appointment date for day matching)
            
        Returns:
            Dict with score, breakdown, and recommendation
        """
        # Get patient and provider details
        patient = self.domain.get_patient(patient_id)
        provider = self.domain.get_provider(provider_id)
        original = self.domain.get_provider(original_provider_id) if original_provider_id else None
        
        # Get appointment if ID provided (for day matching)
        appointment = None
        if appointment_id:
            # Load all appointments from JSON client
            all_appointments = self.domain.json_client._load_json(self.domain.json_client.appointments_file)
            appointment = next((apt for apt in all_appointments if apt.get('appointment_id') == appointment_id), None)
        
        if not patient or not provider:
            return {
                "total_score": 0,
                "breakdown": {},
                "recommendation": "ERROR",
                "error": "Patient or provider not found"
            }
        
        # Scoring logic per USE_CASES.md (Total: 165 points)
        score = 0  # Start from 0
        breakdown = {}
        
        # Factor 1: Continuity Score (40 points) - UC3: Prior provider continuity
        if provider.get('provider_id') in patient.get('prior_providers', []):
            score += 40
            breakdown['prior_provider_continuity'] = 40
        else:
            breakdown['prior_provider_continuity'] = 0
        
        # Factor 2: Specialty Match (35 points)
        patient_specialty = patient.get('condition_specialty_required', '')
        provider_specialty = provider.get('specialty', '')
        if patient_specialty and provider_specialty:
            if patient_specialty.lower() in provider_specialty.lower():
                score += 35
                breakdown['specialty_match'] = 35
            elif 'physical therapy' in provider_specialty.lower():
                # Partial match for general PT
                score += 25
                breakdown['specialty_match'] = 25
            else:
                breakdown['specialty_match'] = 0
        else:
            breakdown['specialty_match'] = 0
        
        # Factor 3: Patient Preference Fit (30 points) - includes gender, location, etc.
        preference_score = 0
        # Gender preference (15 pts)
        patient_gender_pref = patient.get('gender_preference', 'any').lower()
        provider_gender = provider.get('gender', '').lower()
        
        if patient_gender_pref == 'any' or patient_gender_pref == '':
            # Patient has no gender preference - award full points
            preference_score += 15
            breakdown['gender_preference'] = 15
        elif patient_gender_pref == provider_gender:
            # Gender matches patient's preference
            preference_score += 15
            breakdown['gender_preference'] = 15
        else:
            # Gender doesn't match preference
            breakdown['gender_preference'] = 0
        
        # Location/Proximity (15 pts for same zip)
        patient_zip = patient.get('zip', '')
        provider_zip = provider.get('zip', '')
        
        if patient_zip == provider_zip:
            preference_score += 15
            breakdown['proximity_same_zip'] = 15
        else:
            breakdown['proximity_same_zip'] = 0
            
            # Check if patient has max distance restriction
            max_distance = patient.get('max_distance_miles', float('inf'))
            if max_distance < 999:  # Only check if reasonable restriction
                # Calculate approximate distance
                estimated_distance = self.domain.calculate_distance_between_zips(patient_zip, provider_zip)
                
                if estimated_distance > max_distance:
                    # Provider is too far - heavy penalty
                    # Deduct 50 points (makes most matches fail threshold)
                    score -= 50
                    breakdown['distance_penalty'] = -50
                    breakdown['estimated_distance'] = round(estimated_distance, 1)
                    breakdown['max_allowed_distance'] = max_distance
        
        score += preference_score
        breakdown['patient_preference_fit'] = preference_score
        
        # Factor 4: Schedule Load Balance (25 points)
        current_load = provider.get('current_patient_load', 0)
        max_capacity = provider.get('max_patient_capacity', 25)
        if max_capacity > 0:
            utilization = current_load / max_capacity
            if utilization < 0.6:  # < 60% capacity
                score += 25
                breakdown['schedule_load_balance'] = 25
            elif utilization < 0.8:  # 60-80% capacity
                score += 15
                breakdown['schedule_load_balance'] = 15
            else:  # > 80% capacity
                score += 5
                breakdown['schedule_load_balance'] = 5
        else:
            breakdown['schedule_load_balance'] = 0
        
        # Factor 5: Experience Match (20 points) - UC4
        if original:
            # Existing patient - compare to original provider
            if provider.get('years_experience', 0) >= original.get('years_experience', 0):
                score += 20
                breakdown['experience_match'] = 20
            elif provider.get('years_experience', 0) >= (original.get('years_experience', 0) - 2):
                # Within 2 years of original
                score += 15
                breakdown['experience_match'] = 15
            else:
                breakdown['experience_match'] = 0
        else:
            # New patient - award points based on provider's experience level
            provider_exp = provider.get('years_experience', 0)
            if provider_exp >= 10:
                # Senior provider (10+ years)
                score += 20
                breakdown['experience_match'] = 20
            elif provider_exp >= 5:
                # Mid-level provider (5-9 years)
                score += 15
                breakdown['experience_match'] = 15
            elif provider_exp >= 2:
                # Junior provider (2-4 years)
                score += 10
                breakdown['experience_match'] = 10
            else:
                # Very junior (<2 years)
                score += 5
                breakdown['experience_match'] = 5
        
        # Factor 6: Time Slot Priority (15 points, +30 if same provider) - UC2
        slots = provider.get('available_slots', [])
        if slots:
            earliest = min([s.get('time', '23:59') for s in slots if s.get('available', True)])
            # Same provider with earlier slot gets bonus
            if original and provider.get('provider_id') == original.get('provider_id'):
                score += 30
                breakdown['same_provider_earlier_slot'] = 30
            elif earliest < "10:00":  # Morning slot
                score += 15
                breakdown['time_slot_priority'] = 15
            elif earliest < "14:00":  # Early afternoon
                score += 10
                breakdown['time_slot_priority'] = 10
            else:
                breakdown['time_slot_priority'] = 0
        else:
            breakdown['time_slot_priority'] = 0
        
        # Factor 7: Day/Time Match (10 points) - UC5: Preferred day
        # Check if the ACTUAL appointment date matches patient's preferred days
        patient_preferred_days = patient.get('preferred_days', '').split(',')
        patient_preferred_days = [day.strip() for day in patient_preferred_days if day.strip()]
        
        # Check if patient has weekend-only restriction
        weekend_days = {'Saturday', 'Sunday'}
        provider_available_days = set(provider.get('available_days', []))
        
        if patient_preferred_days:
            patient_days_set = set(patient_preferred_days)
            
            # If patient ONLY wants weekends but provider ONLY works weekdays → impossible match
            weekday_days = {'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'}
            if patient_days_set.issubset(weekend_days) and provider_available_days.issubset(weekday_days):
                # Impossible to match - heavy penalty
                score -= 40
                breakdown['impossible_day_match'] = -40
                breakdown['patient_wants_weekends_only'] = True
                breakdown['preferred_day_match'] = 0
                breakdown['matching_days'] = []
            else:
                # Get the day of week from the appointment date
                from datetime import datetime
                appointment_date_str = appointment.get('date', '')
                try:
                    appointment_dt = datetime.fromisoformat(appointment_date_str.replace('Z', '+00:00'))
                    appointment_day = appointment_dt.strftime('%A')  # e.g., "Friday"
                    
                    # Check if appointment day matches patient's preferred days
                    if appointment_day in patient_preferred_days:
                        score += 10
                        breakdown['preferred_day_match'] = 10
                        breakdown['matching_days'] = [appointment_day]
                    else:
                        breakdown['preferred_day_match'] = 0
                        breakdown['matching_days'] = []
                except:
                    breakdown['preferred_day_match'] = 0
                    breakdown['matching_days'] = []
        else:
            breakdown['preferred_day_match'] = 0
            breakdown['matching_days'] = []
        
        # Determine recommendation (based on 165 point max)
        if score >= 100:  # 60% of max (excellent match)
            recommendation = "EXCELLENT"
        elif score >= 80:  # 48% of max (good match)
            recommendation = "GOOD"
        elif score >= 60:  # 36% of max (acceptable match)
            recommendation = "ACCEPTABLE"
        else:  # < 60 points (poor match - needs HOD review)
            recommendation = "POOR"
        
        return {
            "total_score": score,
            "breakdown": breakdown,
            "recommendation": recommendation
        }
    
    def score_and_rank_providers(
        self,
        patient_id: str,
        appointment_id: str,
        qualified_ids: List[str]
    ) -> List[Dict[str, Any]]:
        """
        UC3: Score and rank qualified providers.
        
        Uses LLM to apply scoring rules from knowledge base.
        
        Args:
            patient_id: Patient ID
            appointment_id: Appointment ID
            qualified_ids: List of qualified provider IDs
            
        Returns:
            List of providers with scores, sorted by score (highest first)
        """
        print(f"\n{'='*60}")
        print(f"[UC3: SCORING] Scoring {len(qualified_ids)} qualified providers")
        print(f"{'='*60}")
        
        # Get patient and appointment details
        patient = self.domain.get_patient(patient_id)
        appointment = next((a for a in self.domain.get_affected_appointments("ALL") 
                           if a.get("appointment_id") == appointment_id), None)
        
        # Get provider details
        providers = [self.domain.get_provider(pid) for pid in qualified_ids]
        
        # Get scoring rules from knowledge base
        print(f"[REAL MCP] search_knowledge(query='scoring weights continuity specialty', source='all')")
        scoring_rules = self.knowledge.search_knowledge(
            query="scoring weights continuity specialty",
            source="all"
        )
        
        # Get original provider info for experience/continuity checks
        original_provider = None
        if appointment and appointment.get('provider_id'):
            original_provider = self.domain.get_provider(appointment.get('provider_id'))
        
        # Use LLM to score providers
        if isinstance(self.llm, MockLLM):
            # Mock mode - simple scoring logic
            scores = {}
            for provider in providers:
                score = 50  # Base score
                # Bonus for specialty match
                if provider.get('specialty') == patient.get('condition_specialty_required'):
                    score += 30
                # Bonus for gender match
                if provider.get('gender') == patient.get('gender_preference'):
                    score += 15
                # Bonus for low capacity
                if provider.get('capacity_utilization', 1.0) < 0.7:
                    score += 10
                # Bonus for prior provider continuity
                if provider.get('provider_id') in patient.get('prior_providers', []):
                    score += 25
                # Bonus for experience match (UC4)
                if original_provider and provider.get('years_experience', 0) >= original_provider.get('years_experience', 0):
                    score += 20
                # Bonus for earlier time slots (UC2)
                if provider.get('available_slots'):
                    earliest_slot = min([s.get('time', '23:59') for s in provider.get('available_slots', []) if s.get('available')])
                    if earliest_slot < "10:00":
                        score += 15  # Earlier slot bonus
                    # Extra bonus if same provider with earlier slot
                    if original_provider and provider.get('provider_id') == original_provider.get('provider_id'):
                        score += 30  # Strong continuity + convenience
                scores[provider.get('provider_id')] = score
            print(f"  [Mock] Enhanced scoring: {scores}")
        else:
            # Real LLM mode - use AI reasoning with zip-based proximity
            original_provider_info = ""
            if original_provider:
                original_provider_info = f"""
ORIGINAL PROVIDER (for comparison):
- ID: {original_provider.get('provider_id')}
- Name: {original_provider.get('name')}
- Experience: {original_provider.get('years_experience', 'N/A')} years ({original_provider.get('experience_level', 'N/A')})
- Specialty: {original_provider.get('specialty')}
"""
            
            prompt = f"""You are a healthcare scheduling assistant. Score these providers using ALL 6 priority matching rules.

SCORING RULES:
{scoring_rules}

PATIENT:
- Name: {patient.get('name')}
- Zip Code: {patient.get('zip')}
- Max Distance: {patient.get('max_distance_miles', 10)} miles
- Gender Preference: {patient.get('gender_preference', 'any')}
- Condition: {patient.get('condition')}
- Prior Providers: {patient.get('prior_providers', [])}
- Preferred Days: {patient.get('preferred_days', 'any')}

APPOINTMENT:
{appointment}

{original_provider_info}

PROVIDERS (with experience, time slots, and zip codes):
{providers}

COMPREHENSIVE SCORING FACTORS (6 Use Cases):

1. GENDER PREFERENCE (UC1): +15 points
   - If patient prefers female → female provider gets bonus
   
2. TIME SLOT PRIORITY (UC2): +15 to +30 points
   - Earlier available time slots = +15 points
   - Same provider with earlier slot = +30 bonus (strong continuity!)
   
3. PRIOR PROVIDER CONTINUITY (UC3): +25 points
   - Patient has seen this provider before = relationship bonus
   
4. EXPERIENCE MATCH (UC4): +20 points
   - New provider has >= same years_experience as original provider
   - Compare experience_level (junior < mid-level < senior)
   
5. PREFERRED DAY MATCH (UC5): +10 points
   - Provider available on patient's preferred days
   
6. PROXIMITY (Distance): +20 to -10 points
   - Same zip code = +20 points
   - Adjacent zip codes (1-5 apart) = +10 points
   - Far zip codes (10+ apart) = -10 points
   - Exceeds max_distance_miles = disqualify (score = 0)

ADDITIONAL FACTORS:
- Specialty match = +30 points
- Lower capacity utilization = +10 points (more availability)

Return scores as JSON object like {{"P001": 85, "P004": 40}}.
"""
            response = self.llm.generate(
                prompt=prompt,
                system="You are a healthcare scheduling assistant. Be concise and return only valid JSON.",
                max_tokens=1000,
                temperature=0.3
            )
            
            # Parse response
            import json
            try:
                scores = json.loads(response.content.strip())
            except:
                # Fallback if JSON parsing fails
                print(f"[AGENT] Warning: Failed to parse LLM response, using default scores")
                scores = {pid: 50 for pid in qualified_ids}
        
        # Combine providers with scores
        ranked = []
        for provider in providers:
            provider_id = provider.get("provider_id")
            score = scores.get(provider_id, 0)
            ranked.append({
                "rank": 0,  # Will be set below
                "provider_id": provider_id,
                "provider_name": provider.get("name", "Unknown"),
                "provider": provider,
                "total_score": score,
                "score": score,
                "breakdown": {
                    "specialty": {"score": 35 if provider.get('specialty') == patient.get('condition_specialty_required') else 0, "max": 35},
                    "preference_fit": {"score": 15 if provider.get('gender') == patient.get('gender_preference') else 0, "max": 30},
                    "load_balance": {"score": int(10 * (1 - provider.get('capacity_utilization', 0.5))), "max": 25},
                    "continuity": {"score": 40 if provider_id in patient.get('prior_providers', []) else 0, "max": 40},
                    "day_time_match": {"score": 10, "max": 20}
                },
                "recommendation": "EXCELLENT" if score >= 80 else "GOOD" if score >= 60 else "ACCEPTABLE"
            })
        
        # Sort by score (highest first) and assign ranks
        ranked.sort(key=lambda x: x["total_score"], reverse=True)
        for idx, item in enumerate(ranked, 1):
            item["rank"] = idx
        
        # Print results
        for item in ranked:
            provider_id = item["provider_id"]
            name = item["provider_name"]
            score = item["total_score"]
            print(f"  {item['rank']}. {provider_id} ({name}): {score} points")
        
        print(f"[UC3: SCORING] Ranked {len(ranked)} provider(s)")
        
        # Return structured result for UI
        return {
            "ranked_providers": ranked,
            "recommended_provider_id": ranked[0]["provider_id"] if ranked else None,
            "recommended_provider_name": ranked[0]["provider_name"] if ranked else None,
            "total_candidates": len(ranked)
        }
    
    def create_audit_log(
        self,
        therapist_id: str,
        affected_appointments: List[Dict],
        assignments: List[Dict]
    ) -> Dict[str, Any]:
        """
        UC6: Create audit log of all actions taken.
        
        Args:
            therapist_id: Departing therapist ID
            affected_appointments: List of affected appointments
            assignments: List of provider assignments made
            
        Returns:
            Audit log dictionary
        """
        print(f"\n{'='*60}")
        print(f"[UC6: AUDIT] Generating audit log")
        print(f"{'='*60}")
        
        audit = {
            "therapist_id": therapist_id,
            "appointments_processed": len(affected_appointments),
            "appointments_rebooked": len(assignments),
            "assignments": assignments
        }
        
        print(f"  ✓ Therapist: {therapist_id}")
        print(f"  ✓ Appointments processed: {len(affected_appointments)}")
        print(f"  ✓ Appointments rebooked: {len(assignments)}")
        
        print(f"[UC6: AUDIT] Audit log created")
        
        return audit
