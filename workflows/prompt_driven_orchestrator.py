"""Prompt-Driven Workflow Orchestrator.

This orchestrator uses LangFuse prompts + LLM tool calling to dynamically
manage the workflow, rather than hardcoding logic in Python.

Benefits:
- Update logic by editing prompts (no code deployment)
- A/B test different strategies
- Version control via LangFuse
- Dynamic adaptation based on outcomes
"""

import json
import os
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime

# LangFuse imports
try:
    from langfuse import Langfuse
    LANGFUSE_AVAILABLE = True
except ImportError:
    LANGFUSE_AVAILABLE = False
    print("[ORCHESTRATOR] Warning: LangFuse not available, using local prompts")

# LLM adapter
try:
    from adapters.llm.litellm_adapter import LiteLLMAdapter
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class ToolRegistry:
    """Registry of tools available to the LLM for orchestration."""
    
    def __init__(self, domain_server, patient_engagement_agent, booking_agent):
        self.domain = domain_server
        self.patient_agent = patient_engagement_agent
        self.booking_agent = booking_agent
        
        # Tool function mapping
        self.tools = {
            "get_affected_appointments": self.get_affected_appointments,
            "get_patient_details": self.get_patient_details,
            "get_available_providers": self.get_available_providers,
            "get_provider_details": self.get_provider_details,
            "calculate_match_score": self.calculate_match_score,
            "assign_appointment": self.assign_appointment,
            "send_patient_notification": self.send_patient_notification,
            "add_to_waitlist": self.add_to_waitlist,
        }
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return OpenAI-style tool definitions for LLM."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "get_affected_appointments",
                    "description": "Get list of appointments affected by provider unavailability",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "provider_id": {"type": "string", "description": "Provider ID"},
                            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                        },
                        "required": ["provider_id", "date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_patient_details",
                    "description": "Get patient preferences, history, and requirements",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "Patient ID"}
                        },
                        "required": ["patient_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_available_providers",
                    "description": "Get list of providers available on the given date",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                            "specialty": {"type": "string", "description": "Optional specialty filter"}
                        },
                        "required": ["date"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_provider_details",
                    "description": "Get provider experience, specialties, availability, location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "provider_id": {"type": "string", "description": "Provider ID"}
                        },
                        "required": ["provider_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "calculate_match_score",
                    "description": "Calculate compatibility score between patient and provider using 6 priority matching rules",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "Patient ID"},
                            "provider_id": {"type": "string", "description": "Candidate provider ID"},
                            "original_provider_id": {"type": "string", "description": "Original provider ID for comparison"}
                        },
                        "required": ["patient_id", "provider_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "assign_appointment",
                    "description": "Assign patient appointment to new provider",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "appointment_id": {"type": "string", "description": "Appointment ID"},
                            "new_provider_id": {"type": "string", "description": "New provider ID"},
                            "reason": {"type": "string", "description": "Reason for reassignment"}
                        },
                        "required": ["appointment_id", "new_provider_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "send_patient_notification",
                    "description": "Send notification to patient about reassignment",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "Patient ID"},
                            "appointment_id": {"type": "string", "description": "Appointment ID"},
                            "message": {"type": "string", "description": "Message to send"}
                        },
                        "required": ["patient_id", "appointment_id", "message"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_to_waitlist",
                    "description": "Add patient to waitlist if no suitable provider found",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "patient_id": {"type": "string", "description": "Patient ID"},
                            "appointment_id": {"type": "string", "description": "Appointment ID"},
                            "reason": {"type": "string", "description": "Reason for waitlist"}
                        },
                        "required": ["patient_id", "appointment_id", "reason"]
                    }
                }
            }
        ]
    
    # Tool implementations
    def get_affected_appointments(self, provider_id: str, date: str) -> Dict[str, Any]:
        """Get appointments affected by provider unavailability."""
        appointments = self.domain.get_affected_appointments(provider_id, date)
        return {"appointments": appointments, "count": len(appointments)}
    
    def get_patient_details(self, patient_id: str) -> Dict[str, Any]:
        """Get patient details."""
        patient = self.domain.get_patient(patient_id)
        return patient if patient else {"error": f"Patient {patient_id} not found"}
    
    def get_available_providers(self, date: str, specialty: str = None) -> Dict[str, Any]:
        """Get available providers."""
        providers = self.domain.get_providers()
        # Filter by availability
        available = [p for p in providers if p.get('status') == 'active']
        if specialty:
            available = [p for p in available if specialty.lower() in p.get('specialty', '').lower()]
        return {"providers": available, "count": len(available)}
    
    def get_provider_details(self, provider_id: str) -> Dict[str, Any]:
        """Get provider details."""
        provider = self.domain.get_provider(provider_id)
        return provider if provider else {"error": f"Provider {provider_id} not found"}
    
    def calculate_match_score(self, patient_id: str, provider_id: str, original_provider_id: str = None) -> Dict[str, Any]:
        """Calculate match score using 6-factor scoring."""
        patient = self.domain.get_patient(patient_id)
        provider = self.domain.get_provider(provider_id)
        original = self.domain.get_provider(original_provider_id) if original_provider_id else None
        
        if not patient or not provider:
            return {"error": "Patient or provider not found", "score": 0}
        
        score = 50  # Base score
        factors = {}
        
        # UC1: Gender preference
        if patient.get('gender_preference') == provider.get('gender'):
            score += 15
            factors['gender_preference'] = 15
        
        # UC2: Time slot priority
        slots = provider.get('available_slots', [])
        if slots:
            earliest = min([s.get('time', '23:59') for s in slots if s.get('available')])
            if earliest < "10:00":
                score += 15
                factors['earlier_slot'] = 15
            # Bonus if same provider with earlier slot
            if original and provider.get('provider_id') == original.get('provider_id'):
                score += 30
                factors['same_provider_earlier'] = 30
        
        # UC3: Prior provider continuity
        if provider.get('provider_id') in patient.get('prior_providers', []):
            score += 25
            factors['continuity'] = 25
        
        # UC4: Experience match
        if original and provider.get('years_experience', 0) >= original.get('years_experience', 0):
            score += 20
            factors['experience_match'] = 20
        
        # UC5: Preferred day match
        # (Simplified - would need appointment day info)
        factors['preferred_day'] = 0
        
        # Additional: Specialty match
        if patient.get('condition_specialty_required') == provider.get('specialty'):
            score += 30
            factors['specialty_match'] = 30
        
        # Additional: Proximity
        if patient.get('zip') == provider.get('zip'):
            score += 20
            factors['proximity'] = 20
        
        # Additional: Capacity
        if provider.get('capacity_utilization', 1.0) < 0.7:
            score += 10
            factors['capacity'] = 10
        
        return {
            "score": score,
            "factors": factors,
            "recommendation": "EXCELLENT" if score >= 80 else "GOOD" if score >= 60 else "POOR"
        }
    
    def assign_appointment(self, appointment_id: str, new_provider_id: str, reason: str = None) -> Dict[str, Any]:
        """Assign appointment to new provider."""
        success = self.booking_agent.book_appointment(appointment_id, new_provider_id)
        return {
            "success": success,
            "appointment_id": appointment_id,
            "new_provider_id": new_provider_id,
            "reason": reason
        }
    
    def send_patient_notification(self, patient_id: str, appointment_id: str, message: str) -> Dict[str, Any]:
        """Send notification to patient."""
        # Use email template
        success = self.patient_agent.send_offer(patient_id, appointment_id, message)
        return {"success": success, "patient_id": patient_id}
    
    def add_to_waitlist(self, patient_id: str, appointment_id: str, reason: str) -> Dict[str, Any]:
        """Add patient to waitlist."""
        # Add to waitlist JSON
        success = self.domain.add_to_waitlist(patient_id, appointment_id, reason)
        return {"success": success, "patient_id": patient_id, "reason": reason}
    
    def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool by name with arguments."""
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        tool_func = self.tools[tool_name]
        try:
            result = tool_func(**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}


class PromptDrivenOrchestrator:
    """Orchestrator that uses LangFuse prompts + LLM tool calling."""
    
    def __init__(
        self,
        domain_server,
        patient_engagement_agent,
        booking_agent,
        llm: Optional[Any] = None,
        use_langfuse: bool = True
    ):
        self.domain = domain_server
        self.tool_registry = ToolRegistry(domain_server, patient_engagement_agent, booking_agent)
        
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
                print("[ORCHESTRATOR] LangFuse initialized")
        
        # Initialize LLM
        if llm:
            self.llm = llm
        elif LITELLM_AVAILABLE:
            self.llm = LiteLLMAdapter(
                model=os.getenv("LITELLM_DEFAULT_MODEL", "gpt-oss-20b"),
                api_base=os.getenv("LITELLM_BASE_URL", "http://localhost:4000"),
                api_key=os.getenv("LITELLM_API_KEY", "sk-1234"),
                enable_langfuse=use_langfuse
            )
            print("[ORCHESTRATOR] LiteLLM initialized with tool calling support")
        else:
            raise Exception("LLM required for prompt-driven orchestration")
    
    def get_orchestrator_prompt(self) -> str:
        """Get orchestrator prompt from LangFuse or local file."""
        if self.langfuse:
            try:
                prompt = self.langfuse.get_prompt("healthcare-orchestrator", label="production")
                return prompt.compile()
            except Exception as e:
                print(f"[ORCHESTRATOR] Warning: Could not fetch from LangFuse: {e}")
        
        # Fallback to local prompt file
        from pathlib import Path
        import yaml
        
        prompt_file = Path(__file__).parent.parent / "prompts" / "langfuse_orchestrator_prompts.yaml"
        if prompt_file.exists():
            with open(prompt_file) as f:
                prompts = yaml.safe_load(f)
                return prompts['healthcare_orchestrator']['prompt']
        
        return "You are a healthcare orchestrator. Handle provider unavailability using available tools."
    
    def execute_workflow(self, provider_id: str, date: str, reason: str = "unavailable") -> Dict[str, Any]:
        """Execute the workflow using LLM + tool calling."""
        print(f"\n{'='*60}")
        print(f"[PROMPT-DRIVEN ORCHESTRATOR] Starting workflow")
        print(f"Provider: {provider_id}, Date: {date}, Reason: {reason}")
        print(f"{'='*60}\n")
        
        # Get orchestrator prompt
        system_prompt = self.get_orchestrator_prompt()
        
        # Create initial message
        user_message = f"""
Provider {provider_id} is unavailable on {date} due to: {reason}

Please handle the reassignment of all affected patients using the available tools.
Follow the workflow steps defined in your instructions.
"""
        
        # Track tool calls
        tool_call_history = []
        max_iterations = 20  # Prevent infinite loops
        iteration = 0
        
        # LLM conversation loop with tool calling
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            # Call LLM with tools
            response = self.llm.generate_with_tools(
                messages=messages,
                tools=self.tool_registry.get_tool_definitions(),
                temperature=0.3
            )
            
            # Check if LLM wants to call a tool
            if response.tool_calls:
                # Execute each tool call
                for tool_call in response.tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = json.loads(tool_call['function']['arguments'])
                    
                    print(f"  🔧 Tool Call: {tool_name}({tool_args})")
                    
                    # Execute tool
                    result = self.tool_registry.execute_tool(tool_name, tool_args)
                    print(f"  ✅ Result: {json.dumps(result, indent=2)[:200]}...")
                    
                    # Add to history
                    tool_call_history.append({
                        "tool": tool_name,
                        "arguments": tool_args,
                        "result": result
                    })
                    
                    # Add tool response to messages
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call['id'],
                        "content": json.dumps(result)
                    })
            
            else:
                # LLM is done, return final response
                print(f"\n✅ Workflow complete after {iteration} iterations")
                print(f"   Total tool calls: {len(tool_call_history)}")
                
                # Parse final response
                try:
                    final_result = json.loads(response.content)
                except:
                    final_result = {
                        "message": response.content,
                        "tool_call_history": tool_call_history
                    }
                
                return final_result
        
        # Max iterations reached
        print(f"⚠️  Warning: Max iterations reached")
        return {
            "error": "Max iterations reached",
            "tool_call_history": tool_call_history
        }


# Factory function
def create_prompt_driven_orchestrator(
    domain_server,
    patient_engagement_agent,
    booking_agent,
    llm=None,
    use_langfuse=True
):
    """Create a prompt-driven orchestrator instance."""
    return PromptDrivenOrchestrator(
        domain_server=domain_server,
        patient_engagement_agent=patient_engagement_agent,
        booking_agent=booking_agent,
        llm=llm,
        use_langfuse=use_langfuse
    )

