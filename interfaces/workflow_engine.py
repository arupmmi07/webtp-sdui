"""Abstract workflow engine interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable
from models.workflow import WorkflowState


class WorkflowEngine(ABC):
    """
    Abstract base class for workflow orchestration engines.
    
    Implementations: LangGraphAdapter (recommended), CustomAdapter (simple)
    Orchestrates the 6-stage workflow with state management.
    """
    
    @abstractmethod
    def add_node(self, name: str, func: Callable[[WorkflowState], WorkflowState]):
        """
        Add a node (stage) to the workflow.
        
        Args:
            name: Node name
            func: Function to execute for this node
        """
        pass
    
    @abstractmethod
    def add_edge(self, from_node: str, to_node: str):
        """
        Add an edge between nodes.
        
        Args:
            from_node: Source node
            to_node: Destination node
        """
        pass
    
    @abstractmethod
    def add_conditional_edge(
        self,
        from_node: str,
        condition: Callable[[WorkflowState], str],
        edge_mapping: Dict[str, str]
    ):
        """
        Add a conditional edge that routes based on state.
        
        Args:
            from_node: Source node
            condition: Function that returns the routing key
            edge_mapping: Map of routing keys to destination nodes
        """
        pass
    
    @abstractmethod
    def compile(self) -> Any:
        """
        Compile the workflow graph.
        
        Returns:
            Compiled workflow (implementation-specific)
        """
        pass
    
    @abstractmethod
    async def execute(self, initial_state: WorkflowState) -> WorkflowState:
        """
        Execute the workflow with an initial state.
        
        Args:
            initial_state: Starting workflow state
        
        Returns:
            Final workflow state after all stages complete
        """
        pass
    
    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the name of the workflow engine (e.g., 'langgraph', 'custom')."""
        pass

