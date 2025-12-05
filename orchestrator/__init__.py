"""Workflow Orchestrators - Simple and LangGraph versions.

Provides factory function to create the configured workflow orchestrator.
"""

import sys
from pathlib import Path
from typing import Literal, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Always import simple orchestrator
from orchestrator.workflow import SimpleWorkflowOrchestrator

# Try to import LangGraph orchestrator (might not be available)
try:
    from orchestrator.langgraph_workflow import LangGraphWorkflowOrchestrator
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"[ORCHESTRATOR] Warning: LangGraph not available: {e}")
    LANGGRAPH_AVAILABLE = False
    LangGraphWorkflowOrchestrator = None


def create_workflow_orchestrator(
    engine: Optional[Literal["simple", "langgraph"]] = None,
    smart_scheduling_agent=None,
    patient_engagement_agent=None,
    domain_server=None
):
    """Create workflow orchestrator based on configuration.
    
    Args:
        engine: "simple" or "langgraph" (default: "simple")
            - "simple": Sequential execution (no branching)
            - "langgraph": State machine with conditional branching
        smart_scheduling_agent: Optional agent instance
        patient_engagement_agent: Optional agent instance
        domain_server: Optional domain server instance
    
    Returns:
        Configured orchestrator instance
    """
    if engine is None:
        engine = "simple"
    
    if engine == "langgraph":
        if not LANGGRAPH_AVAILABLE:
            print(f"[ORCHESTRATOR] LangGraph not available, using simple workflow")
            engine = "simple"
        else:
            print(f"[ORCHESTRATOR] Creating LangGraph orchestrator (with branching)")
            return LangGraphWorkflowOrchestrator(
                smart_scheduling_agent=smart_scheduling_agent,
                patient_engagement_agent=patient_engagement_agent,
                domain_server=domain_server
            )
    
    # Default to simple workflow
    print(f"[ORCHESTRATOR] Creating Simple orchestrator (sequential)")
    return SimpleWorkflowOrchestrator(
        smart_scheduling_agent=smart_scheduling_agent,
        patient_engagement_agent=patient_engagement_agent,
        domain_server=domain_server
    )


__all__ = [
    "create_workflow_orchestrator",
    "SimpleWorkflowOrchestrator",
]

if LANGGRAPH_AVAILABLE:
    __all__.append("LangGraphWorkflowOrchestrator")
