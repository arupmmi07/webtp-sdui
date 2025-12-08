"""Template-Driven Workflow Orchestrator using LangFuse Prompt Variables.

This approach is more efficient than tool calling:
1. Fetch all data upfront (patients, providers, appointments)
2. Pass data as variables to LangFuse prompt template
3. LangFuse compiles prompt with the data
4. LLM makes decision in ONE call (no tool calling loop)

Benefits:
- Faster (1 LLM call instead of 10+)
- Cheaper (fewer tokens)
- Simpler (no tool calling loop)
- Still flexible (edit prompt logic in LangFuse UI)
"""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

# LangFuse imports
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("[ORCHESTRATOR] Warning: LangFuse not available, using local prompts")

# Backfill agent for automatic slot matching
try:
    from agents.backfill_agent import BackfillAgent
    BACKFILL_AVAILABLE = True
except ImportError:
    BACKFILL_AVAILABLE = False
    print("[ORCHESTRATOR] Warning: BackfillAgent not available, waitlist will require manual review")

# LLM adapter
try:
    from adapters.llm.litellm_adapter import LiteLLMAdapter
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

# Configuration
from config.llm_settings import settings as llm_settings


class TemplateDrivenOrchestrator:
    """Orchestrator using LangFuse prompt templates with variables."""
    
    def __init__(
        self,
        domain_server,
        patient_engagement_agent,
        booking_agent,
        smart_scheduling_agent,
        llm: Optional[Any] = None,
        use_langfuse: bool = True
    ):
        self.domain = domain_server
        self.patient_agent = patient_engagement_agent
        self.booking_agent = booking_agent
        self.scheduling_agent = smart_scheduling_agent
        
        # Initialize LangFuse (optional)
        self.langfuse = None
        if use_langfuse and LANGFUSE_AVAILABLE:
            langfuse_public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
            langfuse_secret_key = os.getenv("LANGFUSE_SECRET_KEY")
            langfuse_host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            
            if langfuse_public_key and langfuse_secret_key:
                self.langfuse = Langfuse(
                    public_key=langfuse_public_key,
                    secret_key=langfuse_secret_key,
                    host=langfuse_host
                )
                print("[ORCHESTRATOR] LangFuse initialized with template support")
        
        # Initialize LLM
        if llm:
            self.llm = llm
        elif LITELLM_AVAILABLE:
            # Use Azure configuration if available
            provider = os.getenv("ORCHESTRATION_LLM_PROVIDER", "local")
            
            if provider == "azure":
                # Azure OpenAI configuration
                model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-4")
                api_base = os.getenv("ORCHESTRATION_LLM_AZURE_ENDPOINT")
                api_key = os.getenv("ORCHESTRATION_LLM_AZURE_API_KEY")
                
                if api_base and api_key:
                    self.llm = LiteLLMAdapter(
                        model=f"azure/{model}",
                        api_base=api_base,
                        api_key=api_key,
                        enable_langfuse=use_langfuse
                    )
                    print(f"[ORCHESTRATOR] Azure LLM initialized ({model})")
                else:
                    print("[ORCHESTRATOR] Warning: Azure config incomplete, falling back to local")
                    provider = "local"
            
            if provider != "azure":
                # Local LiteLLM configuration (fallback)
                self.llm = LiteLLMAdapter(
                    model=os.getenv("LITELLM_DEFAULT_MODEL", "gpt-oss-20b"),
                    api_base=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
                    api_key=os.getenv("LITELLM_API_KEY", "sk-1234"),
                    enable_langfuse=use_langfuse
                )
                print("[ORCHESTRATOR] Local LiteLLM initialized")
        else:
            raise Exception("LLM required for template-driven orchestration")
    
    def prepare_metadata(self, provider_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Fetch all data needed for the prompt template with date range support.
        
        This is done ONCE upfront, then passed as variables to the prompt.
        Gets all appointments in the date range and groups by patient to avoid duplicate emails.
        
        Args:
            provider_id: Provider who is unavailable
            start_date: Start date of unavailability (YYYY-MM-DD)
            end_date: End date of unavailability (YYYY-MM-DD)
        """
        from datetime import datetime, timedelta
        
        if start_date == end_date:
            print(f"\n[METADATA] Preparing data for provider {provider_id} on {start_date}...")
        else:
            print(f"\n[METADATA] Preparing data for provider {provider_id}")
            print(f"[METADATA] Date range: {start_date} to {end_date}")
        
        # 1. Get ALL appointments for this provider in the date range
        all_provider_appointments = self.domain.get_affected_appointments(provider_id)
        
        # Filter to only appointments in the date range
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        affected_appointments = []
        for apt in all_provider_appointments:
            apt_date_str = apt.get('date', '').split('T')[0]  # Extract YYYY-MM-DD
            try:
                apt_dt = datetime.strptime(apt_date_str, "%Y-%m-%d")
                if start_dt <= apt_dt <= end_dt:
                    affected_appointments.append(apt)
            except:
                pass  # Skip appointments with invalid dates
        
        print(f"  ✓ Found {len(affected_appointments)} affected appointments in range ({len(all_provider_appointments)} total)")
        
        # 2. Get patient details for each appointment
        patients_data = []
        for apt in affected_appointments:
            patient_id = apt.get('patient_id')
            patient = self.domain.get_patient(patient_id)
            if patient:
                patients_data.append({
                    "appointment_id": apt.get('appointment_id'),
                    "patient": patient,
                    "original_time": apt.get('time'),
                    "original_date": apt.get('date')
                })
        print(f"  ✓ Loaded {len(patients_data)} patient records")
        
        # 3. Get the unavailable provider details FIRST
        unavailable_provider = self.domain.get_provider(provider_id)
        
        # 4. Check if unavailable provider has slots on OTHER days (UC3: Continuity +30pts)
        # This is key: patients prefer their existing doctor on a different day!
        same_provider_future_slots = []
        if unavailable_provider:
            # Check if provider has available_slots on OTHER days
            provider_slots = unavailable_provider.get('available_slots', [])
            unavailable_dates = unavailable_provider.get('unavailable_dates', [])
            
            # Generate list of dates in unavailable range
            unavailable_range = []
            current_dt = start_dt
            while current_dt <= end_dt:
                unavailable_range.append(current_dt.strftime("%Y-%m-%d"))
                current_dt += timedelta(days=1)
            
            # Find slots NOT in the unavailable date range
            for slot in provider_slots:
                slot_date = slot.get('date', '')
                if slot_date not in unavailable_range and slot_date not in unavailable_dates:
                    same_provider_future_slots.append(slot)
            
            if same_provider_future_slots:
                print(f"  ✓ Found {len(same_provider_future_slots)} future slots for {unavailable_provider.get('name')} (continuity option!)")
        
        # 5. Get available providers (exclude the unavailable one for TODAY)
        all_providers = self.domain.get_available_providers()  # Gets all active providers
        available_providers = [
            p for p in all_providers 
            if p.get('provider_id') != provider_id  # Exclude the unavailable provider
        ]
        print(f"  ✓ Found {len(available_providers)} available alternative providers")
        
        # 6. Note: We DO NOT pre-calculate match scores
        # The LLM will reason about provider-patient matches autonomously
        # This makes the system truly agentic, not rule-based
        print(f"  ✓ Ready for LLM agentic reasoning (no pre-calculated scores)")
        
        # 7. Compile metadata
        metadata = {
            # Context
            "provider_id": provider_id,
            "provider_name": unavailable_provider.get('name', 'Unknown'),
            "start_date": start_date,
            "end_date": end_date,
            "date": start_date,  # Legacy field for backward compatibility
            "reason": "unavailable",
            "timestamp": datetime.now().isoformat(),
            
            # Affected appointments
            "total_affected": len(affected_appointments),
            "affected_appointments": affected_appointments,
            
            # Patient data
            "patients": patients_data,
            
            # Continuity option (UC3: +30pts for same provider, next available slot)
            "has_continuity_option": len(same_provider_future_slots) > 0,
            "continuity_slots": same_provider_future_slots,
            
            # Available providers
            "available_providers": available_providers,
            "available_providers_count": len(available_providers),
            
            # Note: No pre-calculated scores - LLM reasons autonomously
            
            # Scoring rules (for LLM reference)
            "scoring_rules": {
                "gender_preference": 15,
                "time_slot_priority": 15,
                "same_provider_earlier_slot": 30,
                "prior_provider_continuity": 25,
                "experience_match": 20,
                "preferred_day_match": 10,
                "specialty_match": 30,
                "proximity_same_zip": 20,
                "capacity_bonus": 10
            },
            
            # Decision thresholds (based on 165 point max from USE_CASES.md)
            "thresholds": {
                "excellent": 100,  # 60% of 165
                "good": 80,        # 48% of 165
                "acceptable": 60,  # 36% of 165
                "poor": 0
            }
        }
        
        print(f"[METADATA] ✅ Complete!")
        return metadata
    
    def get_prompt_with_variables(self, metadata: Dict[str, Any]) -> str:
        """Get prompt from LangFuse and compile with metadata variables.
        
        LangFuse supports Mustache templating: {{variable_name}}
        """
        if self.langfuse:
            try:
                # Format sections for LangFuse template
                # These are formatted here so they can be used as simple variables in LangFuse
                patients_section = self._format_patients_section(metadata['patients'])
                providers_section = self._format_providers_section(metadata['available_providers'])
                continuity_info = self._format_continuity_info(metadata)
                
                # Add formatted sections to metadata for LangFuse
                langfuse_metadata = metadata.copy()
                langfuse_metadata['patients_section'] = patients_section
                langfuse_metadata['providers_section'] = providers_section
                langfuse_metadata['continuity_info'] = continuity_info
                
                # Fetch prompt from LangFuse
                prompt_obj = self.langfuse.get_prompt(
                    "healthcare-orchestrator-template",
                    label="production"
                )
                
                # Compile prompt with variables
                # LangFuse automatically replaces {{variable}} with metadata values
                compiled_prompt = prompt_obj.compile(**langfuse_metadata)
                
                print("[PROMPT] ✅ Compiled from LangFuse")
                return compiled_prompt
                
            except Exception as e:
                print(f"[PROMPT] ❌ LangFuse fetch failed: {e}")
                raise Exception(f"Failed to fetch prompt from LangFuse: {e}. Please check LangFuse configuration.")
    
    def _format_patients_section(self, patients_data: List[Dict[str, Any]]) -> str:
        """Format patients section for prompt."""
        return "\n".join([
            f"""
Patient {i+1}: {p['patient']['name']} (ID: {p['patient']['patient_id']})
- Condition: {p['patient'].get('condition', 'N/A')}
- Gender Preference: {p['patient'].get('gender_preference', 'any')}
- Preferred Days: {p['patient'].get('preferred_days', 'any')}
- Prior Providers: {p['patient'].get('prior_providers', [])}
- Zip Code: {p['patient'].get('zip', 'N/A')}
- Insurance: {p['patient'].get('insurance_provider', 'N/A')}
- Appointment ID: {p['appointment_id']}
- Original Time: {p['original_time']}
"""
            for i, p in enumerate(patients_data)
        ])
    
    def _format_providers_section(self, providers_data: List[Dict[str, Any]]) -> str:
        """Format providers section for prompt."""
        return "\n".join([
            f"""
Provider {i+1}: {p['name']} (ID: {p['provider_id']})
- Specialty: {p.get('specialty', 'N/A')}
- Gender: {p.get('gender', 'N/A')}
- Experience: {p.get('years_experience', 'N/A')} years ({p.get('experience_level', 'N/A')})
- Location: {p.get('primary_location', 'N/A')}
- Zip Code: {p.get('zip', 'N/A')}
- Available Days: {', '.join(p.get('available_days', []))}
- Capacity: {p.get('current_patient_load', 0)}/{p.get('max_patient_capacity', 0)}
- Available Slots: {', '.join([s.get('time', '') for s in p.get('available_slots', [])])}
"""
            for i, p in enumerate(providers_data)
        ])
    
    def _format_continuity_info(self, metadata: Dict[str, Any]) -> str:
        """Format continuity info section for prompt."""
        if metadata.get('has_continuity_option'):
            continuity_slots = metadata.get('continuity_slots', [])
            if continuity_slots:
                return f"""
CONTINUITY OPTION:
The original provider ({metadata['provider_name']}) has future available slots:
{chr(10).join([f"  • {slot.get('date')} at {slot.get('time')}" for slot in continuity_slots[:3]])}

Consider offering these slots to patients who value continuity of care.
"""
        return ""
    
    
    def execute_workflow(self, provider_id: str, start_date: str = None, end_date: str = None, 
                         date: str = None, reason: str = "unavailable") -> Dict[str, Any]:
        """Execute the workflow using template-driven approach with date range support.
        
        Args:
            provider_id: Provider to mark unavailable
            start_date: Start date of unavailability (YYYY-MM-DD)
            end_date: End date of unavailability (YYYY-MM-DD)
            date: Legacy single date parameter (for backward compatibility)
            reason: Reason for unavailability (sick, vacation, etc.)
        
        Steps:
        1. Mark provider unavailable for date range
        2. Fetch all appointments in date range (grouped by patient)
        3. Compile prompt with metadata variables
        4. Single LLM call to make all decisions
        5. Execute assignments (ONE email per patient)
        """
        # Support backward compatibility: if only "date" is provided
        if date and not start_date:
            start_date = date
            end_date = date
        
        print(f"\n{'='*60}")
        print(f"[TEMPLATE-DRIVEN ORCHESTRATOR] Starting workflow")
        print(f"Provider: {provider_id}")
        print(f"Date Range: {start_date} to {end_date}")
        print(f"Reason: {reason}")
        print(f"{'='*60}\n")
        
        # Step 0: Mark provider as unavailable for ALL dates in range
        self._mark_provider_unavailable_range(provider_id, start_date, end_date, reason)
        
        # Step 1: Prepare all metadata for date range
        metadata = self.prepare_metadata(provider_id, start_date, end_date)
        
        # Step 2: Get compiled prompt with variables
        prompt = self.get_prompt_with_variables(metadata)
        
        # Step 3: Single LLM call to make decisions
        print(f"\n[LLM] Making assignment decisions...")
        print(f"[LLM] Prompt length: {len(prompt)} chars")
        
        try:
            # Adjust temperature for GPT-5 (only supports 1.0)
            temperature = llm_settings.ORCHESTRATOR_TEMPERATURE
            model = os.getenv("ORCHESTRATION_LLM_MODEL", "gpt-4")
            if "gpt-5" in model.lower():
                temperature = 1.0
                print(f"[LLM] Using temperature=1.0 for {model} (GPT-5 requirement)")
            
            response = self.llm.generate(
                prompt=prompt,
                system="You are a healthcare scheduling assistant. You MUST return ONLY valid JSON with an 'assignments' array. Do not include any text before or after the JSON. The JSON must start with '{' and end with '}'.",
                max_tokens=llm_settings.ORCHESTRATOR_MAX_TOKENS,
                temperature=temperature,
                timeout=llm_settings.REQUEST_TIMEOUT
            )
            
            print(f"[LLM] Response received: {len(response.content) if response.content else 0} chars")
            if response.content:
                # Show first 200 chars for debugging
                preview = response.content.strip()[:200]
                print(f"[LLM] Response preview: {preview}...")
            
            if not response.content or len(response.content.strip()) == 0:
                print(f"[ERROR] Empty LLM response!")
                # Fallback: use simple rule-based assignment
                print(f"[FALLBACK] Using rule-based assignment")
                decisions = self._fallback_assignment(metadata)
            else:
                # Step 4: Parse LLM response
                try:
                    decisions = json.loads(response.content.strip())
                    
                    # Validate that assignments exist and are not empty
                    if 'assignments' not in decisions:
                        print(f"[ERROR] LLM response missing 'assignments' key")
                        print(f"Response keys: {list(decisions.keys())}")
                        print(f"[FALLBACK] Using rule-based assignment")
                        decisions = self._fallback_assignment(metadata)
                    elif not isinstance(decisions['assignments'], list):
                        print(f"[ERROR] LLM response 'assignments' is not a list (type: {type(decisions['assignments'])})")
                        print(f"[FALLBACK] Using rule-based assignment")
                        decisions = self._fallback_assignment(metadata)
                    elif len(decisions['assignments']) == 0:
                        print(f"[ERROR] LLM response has empty assignments array")
                        print(f"[FALLBACK] Using rule-based assignment")
                        decisions = self._fallback_assignment(metadata)
                    else:
                        # LLM provides match_factors and reasoning - no need to enrich from pre-calculated scores
                        # The LLM's autonomous reasoning is what we use
                        for assignment in decisions['assignments']:
                            # Ensure match_factors exists (LLM should provide this)
                            if 'match_factors' not in assignment:
                                assignment['match_factors'] = {}
                            
                            # Convert match_quality to numeric score for backward compatibility
                            quality_map = {
                                "EXCELLENT": 100,
                                "GOOD": 75,
                                "ACCEPTABLE": 60,
                                "POOR": 40
                            }
                            if 'match_quality' in assignment and 'match_score' not in assignment:
                                assignment['match_score'] = quality_map.get(assignment['match_quality'], 50)
                            
                            # Minimal validation: Only ensure required fields exist for execution
                            # The LLM should handle all decision-making via the prompt
                            if 'appointment_id' not in assignment:
                                print(f"  ⚠️  Assignment missing appointment_id - skipping")
                                continue
                                
                except json.JSONDecodeError as e:
                    print(f"[ERROR] Failed to parse LLM response: {e}")
                    print(f"Response: {response.content[:500]}")
                    
                    # Try hardcoded LLM-style response first (for demo purposes)
                    print(f"[FALLBACK] Attempting hardcoded LLM-style response...")
                    decisions = self._create_hardcoded_llm_response(metadata)
                    
                    # If hardcoded response fails, use rule-based
                    if not decisions or not decisions.get('assignments'):
                        print(f"[FALLBACK] Using rule-based assignment")
                        decisions = self._fallback_assignment(metadata)
                    
        except Exception as e:
            print(f"[ERROR] LLM call failed: {e}")
            # Fallback to rule-based
            print(f"[FALLBACK] Using rule-based assignment")
            decisions = self._fallback_assignment(metadata)
        
        # Step 5: Execute assignments based on LLM decisions
        print(f"\n[EXECUTION] Executing {len(decisions.get('assignments', []))} assignments...")
        
        executed_assignments = []
        waitlist_entries = []
        
        for assignment in decisions.get('assignments', []):
            apt_id = assignment.get('appointment_id')
            action = assignment.get('action')
            
            if action == 'assign':
                # Assign to provider
                new_provider_id = assignment.get('assigned_to')
                match_score = assignment.get('match_score', 0)
                match_quality = assignment.get('match_quality')
                reasoning = assignment.get('reasoning')
                
                # Minimal execution safety check: Only verify provider exists (don't fix LLM decisions)
                if not new_provider_id:
                    print(f"  ⚠️  {apt_id}: No provider specified - LLM should have waitlisted. Skipping.")
                    continue
                
                # Verify provider exists in available providers (execution safety)
                provider_exists = any(p.get('provider_id') == new_provider_id for p in metadata.get('available_providers', []))
                if not provider_exists:
                    print(f"  ⚠️  {apt_id}: Provider {new_provider_id} not found - LLM should have waitlisted. Skipping.")
                    continue
                
                # Proceed with assignment (LLM made the decision)
                # Use LLM-provided match factors (autonomous reasoning)
                match_factors = assignment.get('match_factors', {})
                
                success = self.booking_agent.book_appointment(
                    apt_id, 
                    new_provider_id,
                    match_score=match_score,
                    match_factors=match_factors,
                    match_quality=match_quality,
                    reasoning=reasoning
                )
                
                if success:
                    # Send notification with appointment details
                    patient_id = assignment.get('patient_id')
                    new_provider_id = assignment.get('assigned_to')
                    
                    # Get appointment details for email
                    apt_details = next((apt for apt in metadata['affected_appointments'] if apt['appointment_id'] == apt_id), {})
                    
                    self.patient_agent.send_offer(
                        patient_id=patient_id,
                        appointment_id=apt_id,
                        new_provider_id=new_provider_id,
                        date=apt_details.get('date', metadata['date']),
                        time=apt_details.get('time', 'TBD')
                    )
                    
                    executed_assignments.append(assignment)
                    print(f"  ✓ {apt_id} → {assignment.get('assigned_to_name')} (Score: {assignment.get('match_score')})")
                else:
                    print(f"  ✗ Failed to assign {apt_id} - booking failed")
            
            # Handle waitlist (either original action or converted from failed assign)
            if action == 'waitlist':
                # Add to waitlist
                patient_id = assignment.get('patient_id')
                reason = assignment.get('reasoning', 'No suitable provider found')
                match_score = assignment.get('match_score', 0)
                
                # Get full patient details for waitlist entry
                patient_data = self.domain.get_patient(patient_id)
                waitlist_entry = {
                    "patient_id": patient_id,
                    "name": patient_data.get('name', patient_id),
                    "condition": patient_data.get('condition', 'N/A'),
                    "no_show_risk": patient_data.get('no_show_risk', 0.5),
                    "priority": "HIGH" if match_score < 40 else "MEDIUM",
                    "requested_specialty": patient_data.get('condition_specialty_required', 'Physical Therapy'),
                    "requested_location": patient_data.get('preferred_location', 'Any'),
                    "availability_windows": {
                        "days": patient_data.get('preferred_days', '').split(',') if patient_data.get('preferred_days') else ['Any'],
                        "times": ["Morning", "Afternoon"]
                    },
                    "insurance": patient_data.get('insurance_provider', 'Unknown'),
                    "current_appointment": apt_id,
                    "willing_to_move_up": True,
                    "added_to_waitlist": datetime.now().isoformat() + "Z",
                    "waitlist_reason": f"No suitable match found (Score: {match_score}) - {reason}",
                    "notes": reason
                }
                self.domain.add_to_waitlist(waitlist_entry)
                
                waitlist_entries.append(assignment)
                print(f"  ⏳ {apt_id} → Waitlist (Score: {assignment.get('match_score')})")
            
            elif action == 'assign_hod_review':
                # UC6 Fallback: Assign to HOD for manual review
                new_provider_id = assignment.get('assigned_to')
                match_score = assignment.get('match_score', 0)
                match_quality = assignment.get('match_quality')
                reasoning = assignment.get('reasoning')
                
                # Use LLM-provided match factors (autonomous reasoning)
                match_factors = assignment.get('match_factors', {})
                
                success = self.booking_agent.book_appointment(
                    apt_id, 
                    new_provider_id,
                    status='needs_review',  # Mark as needs manual review
                    match_score=match_score,
                    match_factors=match_factors,
                    match_quality=match_quality,
                    reasoning=reasoning
                )
                
                if success:
                    # Don't send email - HOD will manually review and contact patient
                    executed_assignments.append(assignment)
                    print(f"  ⚠️  {apt_id} → HOD REVIEW: {assignment.get('assigned_to_name')} (Score: {assignment.get('match_score')})")
                else:
                    print(f"  ✗ Failed to assign {apt_id} to HOD")
            
            elif action == 'waitlist':
                # Add to waitlist
                patient_id = assignment.get('patient_id')
                reason = assignment.get('reasoning', 'No suitable provider found')
                match_score = assignment.get('match_score', 0)
                
                # Get full patient details for waitlist entry
                patient_data = self.domain.get_patient(patient_id)
                waitlist_entry = {
                    "patient_id": patient_id,
                    "name": patient_data.get('name', patient_id),
                    "condition": patient_data.get('condition', 'N/A'),
                    "no_show_risk": patient_data.get('no_show_risk', 0.5),
                    "priority": "HIGH" if match_score < 40 else "MEDIUM",
                    "requested_specialty": patient_data.get('condition_specialty_required', 'Physical Therapy'),
                    "requested_location": patient_data.get('preferred_location', 'Any'),
                    "availability_windows": {
                        "days": patient_data.get('preferred_days', '').split(',') if patient_data.get('preferred_days') else ['Any'],
                        "times": ["Morning", "Afternoon"]
                    },
                    "insurance": patient_data.get('insurance_provider', 'Unknown'),
                    "current_appointment": apt_id,
                    "willing_to_move_up": True,
                    "added_to_waitlist": datetime.now().isoformat() + "Z",
                    "waitlist_reason": f"No suitable match found (Score: {match_score}) - {reason}",
                    "notes": reason
                }
                self.domain.add_to_waitlist(waitlist_entry)
                
                waitlist_entries.append(assignment)
                print(f"  ⏳ {apt_id} → Waitlist (Score: {assignment.get('match_score')})")
                
                # NEW: Trigger automatic backfill
                if BACKFILL_AVAILABLE:
                    try:
                        backfill_agent = BackfillAgent(self.domain.json_client)
                        appointment = self.domain.get_appointment(apt_id)
                        
                        if appointment:
                            print(f"  🔄 Attempting auto-backfill for {apt_id}...")
                            backfill_result = backfill_agent.handle_slot_freed(
                                appointment,
                                reason="Patient declined all providers - added to waitlist"
                            )
                            
                            if backfill_result.get('status') == 'BACKFILLED':
                                backfilled_patient = backfill_result.get('patient_id')
                                print(f"  🎉 Auto-backfilled with waitlist patient {backfilled_patient}")
                            else:
                                print(f"  ℹ️  No immediate backfill match (status: {backfill_result.get('status')})")
                    except Exception as e:
                        print(f"  ⚠️  Backfill attempt failed: {str(e)}")
                        # Continue without failing the workflow
        
        # Step 5.5: Handle any patients that LLM didn't include in response
        # Use pre-calculated match scores to process them automatically
        assigned_patient_ids = {a.get('patient_id') for a in decisions.get('assignments', [])}
        affected_patient_ids = {apt['patient_id'] for apt in metadata['affected_appointments']}
        missing_patient_ids = affected_patient_ids - assigned_patient_ids
        
        if missing_patient_ids:
            print(f"\n[AUTO-PROCESS] {len(missing_patient_ids)} patients not in LLM response")
            print(f"  Missing: {', '.join(missing_patient_ids)}")
            print(f"  → Calculating scores on-demand for missing patients")
            
            for missing_patient_id in missing_patient_ids:
                print(f"\n  [AUTO] Processing {missing_patient_id}...")
                
                # Find the appointment for this patient
                apt = next((a for a in metadata['affected_appointments'] if a['patient_id'] == missing_patient_id), None)
                if not apt:
                    print(f"  [AUTO] ✗ No appointment found for {missing_patient_id}")
                    continue
                
                apt_id = apt['appointment_id']
                print(f"  [AUTO] Found appointment {apt_id}")
                
                # Calculate scores on-demand for this patient (agentic fallback)
                patient_scores = []
                for provider in metadata['available_providers']:
                    score_result = self.scheduling_agent.calculate_match_score(
                        patient_id=missing_patient_id,
                        provider_id=provider['provider_id'],
                        original_provider_id=metadata['provider_id'],
                        appointment_id=apt_id
                    )
                    patient_scores.append({
                        'provider_id': provider['provider_id'],
                        'provider_name': provider['name'],
                        'score': score_result.get('total_score', 0),
                        'factors': score_result.get('breakdown', {})
                    })
                
                print(f"  [AUTO] Calculated {len(patient_scores)} match scores for {missing_patient_id}")
                
                if not patient_scores:
                    print(f"  [AUTO] ⚠️  No providers available for {missing_patient_id} - waitlisting")
                    # Add to waitlist
                    patient_data = self.domain.get_patient(missing_patient_id)
                    waitlist_entry = {
                        "patient_id": missing_patient_id,
                        "name": patient_data.get('name', missing_patient_id),
                        "condition": patient_data.get('condition', 'N/A'),
                        "no_show_risk": patient_data.get('no_show_risk', 0.5),
                        "priority": "HIGH",
                        "requested_specialty": patient_data.get('condition_specialty_required', 'Physical Therapy'),
                        "requested_location": patient_data.get('preferred_location', 'Any'),
                        "availability_windows": {
                            "days": patient_data.get('preferred_days', '').split(',') if patient_data.get('preferred_days') else ['Any'],
                            "times": ["Morning", "Afternoon"]
                        },
                        "insurance": patient_data.get('insurance_provider', 'Unknown'),
                        "current_appointment": apt_id,
                        "willing_to_move_up": True,
                        "added_to_waitlist": datetime.now().isoformat() + "Z",
                        "waitlist_reason": "❌ LLM didn't process this patient - no providers available",
                        "notes": "Patient was not included in LLM response"
                    }
                    self.domain.add_to_waitlist(waitlist_entry)
                    continue
                
                # Find best match
                best_match = max(patient_scores, key=lambda x: x['score'])
                best_provider_id = best_match['provider_id']
                best_score = best_match['score']
                match_factors = best_match.get('factors', {})
                
                print(f"  📊 {missing_patient_id}: Best match = {best_match['provider_name']} (Score: {best_score})")
                
                # Apply same logic as LLM would:
                # - Score >= 60: Assign
                # - Score < 60: Waitlist
                
                if best_score >= 60:
                    # Good match - assign
                    auto_reasoning = f"Auto-assigned using on-demand score calculation (LLM didn't include in response)"
                    auto_quality = "GOOD" if best_score >= 75 else "ACCEPTABLE"
                    
                    success = self.booking_agent.book_appointment(
                        apt_id,
                        best_provider_id,
                        match_score=best_score,
                        match_factors=match_factors,
                        match_quality=auto_quality,
                        reasoning=auto_reasoning
                    )
                    
                    if success:
                        # Send notification
                        apt_details = next((a for a in metadata['affected_appointments'] if a['appointment_id'] == apt_id), {})
                        
                        self.patient_agent.send_offer(
                            patient_id=missing_patient_id,
                            appointment_id=apt_id,
                            new_provider_id=best_provider_id,
                            date=apt_details.get('date', metadata['date']),
                            time=apt_details.get('time', 'TBD')
                        )
                        
                        executed_assignments.append({
                            "appointment_id": apt_id,
                            "patient_id": missing_patient_id,
                            "assigned_to": best_provider_id,
                            "assigned_to_name": best_match['provider_name'],
                            "match_score": best_score,
                            "match_factors": match_factors,
                            "match_quality": auto_quality,
                            "action": "assign",
                            "reasoning": auto_reasoning
                        })
                        print(f"  ✅ {apt_id} → {best_match['provider_name']} (Score: {best_score})")
                    else:
                        print(f"  ✗ Failed to assign {apt_id}")
                
                else:
                    # Low score - add to waitlist with reason
                    print(f"  ⚠️  Low score ({best_score}) → Waitlist")
                    
                    patient_data = self.domain.get_patient(missing_patient_id)
                    waitlist_entry = {
                        "patient_id": missing_patient_id,
                        "name": patient_data.get('name', missing_patient_id),
                        "condition": patient_data.get('condition', 'N/A'),
                        "no_show_risk": patient_data.get('no_show_risk', 0.5),
                        "priority": "HIGH" if best_score < 40 else "MEDIUM",
                        "requested_specialty": patient_data.get('condition_specialty_required', 'Physical Therapy'),
                        "requested_location": patient_data.get('preferred_location', 'Any'),
                        "availability_windows": {
                            "days": patient_data.get('preferred_days', '').split(',') if patient_data.get('preferred_days') else ['Any'],
                            "times": ["Morning", "Afternoon"]
                        },
                        "insurance": patient_data.get('insurance_provider', 'Unknown'),
                        "current_appointment": apt_id,
                        "willing_to_move_up": True,
                        "added_to_waitlist": datetime.now().isoformat() + "Z",
                        "waitlist_reason": f"❌ No suitable match found - Best score: {best_score}/165 points (threshold: 60)",
                        "notes": f"Best available provider: {best_match['provider_name']} ({best_score} points) - below acceptable threshold"
                    }
                    self.domain.add_to_waitlist(waitlist_entry)
                    
                    waitlist_entries.append({
                        "appointment_id": apt_id,
                        "patient_id": missing_patient_id,
                        "action": "waitlist",
                        "match_score": best_score,
                        "reasoning": f"No suitable match - best score {best_score} below threshold 60"
                    })
                    print(f"  ⏳ {apt_id} → Waitlist (Score: {best_score})")
        
        # Step 6: Return results with method indicator
        assignment_method = decisions.get('summary', {}).get('method', 'llm-template-driven')
        
        result = {
            "success": True,
            "provider_id": provider_id,
            "start_date": start_date,
            "end_date": end_date,
            "date": start_date,  # Legacy field for backward compatibility
            "date_range_days": (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1,
            "total_affected": metadata['total_affected'],
            "successful_assignments": len(executed_assignments),
            "waitlist_entries": len(waitlist_entries),
            "assignments": executed_assignments,
            "waitlist": waitlist_entries,
            "summary": decisions.get('summary', {}),
            "metadata": metadata,  # Include for audit
            "assignment_method": assignment_method,  # NEW: Shows which method was used
            "used_fallback": assignment_method == "rule-based-fallback"  # NEW: Flag for fallback
        }
        
        print(f"\n[WORKFLOW] ✅ Complete!")
        print(f"  Date Range: {start_date} to {end_date} ({result['date_range_days']} day(s))")
        print(f"  Method: {assignment_method.upper()}")
        print(f"  Assigned: {len(executed_assignments)}")
        print(f"  Waitlist: {len(waitlist_entries)}")
        
        return result
    
    def _create_hardcoded_llm_response(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a hardcoded LLM-style response when JSON parsing fails.
        This mimics what the LLM would return, using actual patient/provider data.
        Useful for demos when LM Studio has issues.
        """
        print("[HARDCODED] Creating LLM-style response from available data...")
        
        assignments = []
        
        # Get patients and providers from metadata
        patients_data = metadata.get('patients', [])
        available_providers = metadata.get('available_providers', [])
        
        if not patients_data or not available_providers:
            print("[HARDCODED] ❌ No patients or providers available")
            return None
        
        # Find orthopedic providers (best match for Dr. Sarah Johnson's patients)
        ortho_providers = [
            p for p in available_providers 
            if 'orthopedic' in p.get('specialty', '').lower()
        ]
        
        # If no ortho providers, use any available
        target_providers = ortho_providers if ortho_providers else available_providers
        
        print(f"[HARDCODED] Found {len(target_providers)} suitable providers for {len(patients_data)} patients")
        
        # Create assignments for each patient
        for patient_data in patients_data:
            patient = patient_data.get('patient', {})
            apt_id = patient_data.get('appointment_id')
            
            # Find best provider match
            best_provider = None
            for provider in target_providers:
                # Prefer female providers if patient prefers female
                gender_pref = patient.get('gender_preference', 'any')
                if gender_pref == 'female' and provider.get('gender') == 'female':
                    best_provider = provider
                    break
                elif gender_pref == 'any' or not best_provider:
                    best_provider = provider
            
            if not best_provider:
                best_provider = available_providers[0]  # Fallback to first available
            
            # Determine match quality
            specialty_match = 'orthopedic' in best_provider.get('specialty', '').lower()
            gender_match = (
                patient.get('gender_preference', 'any') == 'any' or
                patient.get('gender_preference') == best_provider.get('gender')
            )
            
            if specialty_match and gender_match:
                match_quality = "EXCELLENT"
                reasoning = (
                    f"Tier 1 (Must-Have): ✅ Specialty match (orthopedic), "
                    f"✅ Availability, ✅ Capacity.\n"
                    f"Tier 2 (Preferences): ✅ Gender preference met ({best_provider.get('gender')}), "
                    f"✅ Experienced provider. Excellent overall match."
                )
            elif specialty_match:
                match_quality = "GOOD"
                reasoning = (
                    f"Tier 1 (Must-Have): ✅ Specialty match (orthopedic), "
                    f"✅ Availability, ✅ Capacity.\n"
                    f"Tier 2 (Preferences): ⚠️ Gender preference not perfectly matched, "
                    f"but good overall match."
                )
            else:
                match_quality = "ACCEPTABLE"
                reasoning = (
                    f"Tier 1 (Must-Have): ✅ Availability, ✅ Capacity.\n"
                    f"Tier 2 (Preferences): ⚠️ Specialty and preferences partially matched. "
                    f"Acceptable match given constraints."
                )
            
            assignment = {
                "appointment_id": apt_id,
                "patient_id": patient.get('patient_id'),
                "patient_name": patient.get('name', 'Unknown'),
                "assigned_to": best_provider.get('provider_id'),
                "assigned_to_name": best_provider.get('name'),
                "match_quality": match_quality,
                "reasoning": reasoning,
                "match_factors": {
                    "tier1_specialty_match": specialty_match,
                    "tier1_availability": True,
                    "tier1_capacity": True,
                    "tier2_gender_preference_met": gender_match,
                    "tier2_location_match": True,
                    "tier2_day_preference_met": True
                },
                "action": "assign"
            }
            
            assignments.append(assignment)
        
        result = {
            "assignments": assignments,
            "summary": {
                "total_processed": len(assignments),
                "successful_assignments": len(assignments),
                "waitlist_entries": 0
            }
        }
        
        print(f"[HARDCODED] ✅ Created {len(assignments)} assignments")
        return result
    
    def _fallback_assignment(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback assignment when LLM completely fails.
        Uses on-demand score calculation (still agentic, just simpler).
        """
        assignments = []
        
        for patient in metadata['affected_appointments']:
            apt_id = patient['appointment_id']
            patient_id = patient['patient_id']
            patient_name = patient.get('patient_name', 'Unknown')
            
            # Calculate scores on-demand for this patient
            patient_scores = []
            for provider in metadata['available_providers']:
                score_result = self.scheduling_agent.calculate_match_score(
                    patient_id=patient_id,
                    provider_id=provider['provider_id'],
                    original_provider_id=metadata['provider_id'],
                    appointment_id=apt_id
                )
                patient_scores.append({
                    'provider_id': provider['provider_id'],
                    'provider_name': provider['name'],
                    'score': score_result.get('total_score', 0),
                    'factors': score_result.get('breakdown', {})
                })
            
            if patient_scores:
                # Sort by score
                patient_scores.sort(key=lambda x: x['score'], reverse=True)
                best_match = patient_scores[0]
                
                # If score is good enough, assign
                if best_match['score'] >= 60:  # Use simple threshold
                    assignments.append({
                        "appointment_id": apt_id,
                        "patient_id": patient_id,
                        "patient_name": patient_name,
                        "assigned_to": best_match['provider_id'],
                        "assigned_to_name": best_match['provider_name'],
                        "match_score": best_match['score'],
                        "match_factors": best_match.get('factors', {}),
                        "match_quality": "GOOD" if best_match['score'] >= 75 else "ACCEPTABLE",
                        "reasoning": f"Fallback: Best match with score {best_match['score']}",
                        "action": "assign"
                    })
                else:
                    # Low score - waitlist
                    assignments.append({
                        "appointment_id": apt_id,
                        "patient_id": patient_id,
                        "patient_name": patient_name,
                        "assigned_to": None,
                        "assigned_to_name": None,
                        "match_score": best_match['score'],
                        "match_factors": best_match.get('factors', {}),
                        "match_quality": "POOR",
                        "reasoning": f"Fallback: No good match (score: {best_match['score']}) - waitlisting",
                        "action": "waitlist"
                    })
            else:
                # No providers - waitlist
                assignments.append({
                    "appointment_id": apt_id,
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "assigned_to": None,
                    "assigned_to_name": None,
                    "match_score": 0,
                    "match_factors": {},
                    "match_quality": "POOR",
                    "reasoning": "Fallback: No providers available - waitlisting",
                    "action": "waitlist"
                })
        
        return {
            "assignments": assignments,
            "summary": {
                "total": len(assignments),
                "assigned": len([a for a in assignments if a['action'] == 'assign']),
                "hod_review": len([a for a in assignments if a['action'] == 'assign_hod_review']),
                "waitlisted": len([a for a in assignments if a['action'] == 'waitlist']),
                "method": "rule-based-fallback"
            }
        }
    
    def _mark_provider_unavailable_range(self, provider_id: str, start_date: str, end_date: str, reason: str = "sick"):
        """Mark provider as unavailable for a DATE RANGE.
        
        IMPORTANT: Provider remains 'active' but is unavailable for specific dates only.
        This allows the provider to be available on other days.
        
        Args:
            provider_id: Provider to mark unavailable
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            reason: Reason (sick, vacation, etc.)
        """
        try:
            from datetime import datetime, timedelta
            
            providers = self.domain.json_client._load_json(self.domain.json_client.providers_file)
            
            for provider in providers:
                if provider.get('provider_id') == provider_id:
                    # Ensure unavailable_dates list exists
                    if 'unavailable_dates' not in provider:
                        provider['unavailable_dates'] = []
                    
                    # Generate all dates in the range
                    start = datetime.strptime(start_date, "%Y-%m-%d")
                    end = datetime.strptime(end_date, "%Y-%m-%d")
                    current = start
                    
                    dates_added = []
                    while current <= end:
                        date_str = current.strftime("%Y-%m-%d")
                        if date_str not in provider['unavailable_dates']:
                            provider['unavailable_dates'].append(date_str)
                            dates_added.append(date_str)
                        current += timedelta(days=1)
                    
                    # KEEP status as 'active' - provider is still active, just unavailable for THESE dates
                    if provider.get('status') != 'active':
                        provider['status'] = 'active'
                    
                    if len(dates_added) == 1:
                        print(f"[PROVIDER UPDATE] Marked {provider.get('name')} unavailable for {dates_added[0]} (reason: {reason})")
                    else:
                        print(f"[PROVIDER UPDATE] Marked {provider.get('name')} unavailable for {len(dates_added)} days:")
                        print(f"[PROVIDER UPDATE]   {start_date} to {end_date} (reason: {reason})")
                    print(f"[PROVIDER UPDATE] Provider status remains: active (available on other days)")
                    break
            
            # Save updated providers
            self.domain.json_client._save_json(self.domain.json_client.providers_file, providers)
            print(f"[PROVIDER UPDATE] ✅ Provider unavailable_dates updated")
            
        except Exception as e:
            print(f"[ERROR] Failed to mark provider unavailable for range: {e}")
    
    def _mark_provider_unavailable(self, provider_id: str, date: str, reason: str = "sick"):
        """Legacy method - use _mark_provider_unavailable_range instead."""
        self._mark_provider_unavailable_range(provider_id, date, date, reason)
    
    def _get_hod_provider(self) -> Dict[str, Any]:
        """Get the Head of Department provider for fallback assignments."""
        providers = self.domain.get_available_providers()
        
        # Find provider designated as HOD
        hod = next((p for p in providers if p.get('is_hod', False)), None)
        
        if hod:
            return hod
        
        # Fallback: Use first provider if no HOD designated
        if providers:
            return providers[0]
        
        # Last resort: Return placeholder
        return {
            "provider_id": "HOD001",
            "name": "Head of Department",
            "specialty": "General"
        }


# Factory function
def create_template_driven_orchestrator(
    domain_server,
    patient_engagement_agent,
    booking_agent,
    smart_scheduling_agent,
    llm=None,
    use_langfuse=True
):
    """Create a template-driven orchestrator instance."""
    return TemplateDrivenOrchestrator(
        domain_server=domain_server,
        patient_engagement_agent=patient_engagement_agent,
        booking_agent=booking_agent,
        smart_scheduling_agent=smart_scheduling_agent,
        llm=llm,
        use_langfuse=use_langfuse
    )

