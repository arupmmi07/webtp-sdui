"""Abstract LLM provider interface for vendor-agnostic LLM interaction."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class ToolCall:
    """Represents a tool call from the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class LLMResponse:
    """Standard LLM response format."""
    content: str
    tool_calls: List[ToolCall] = None
    stop_reason: str = "end_turn"
    usage: Dict[str, int] = None  # tokens_used, etc.
    
    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.usage is None:
            self.usage = {}


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    Implementations: AnthropicAdapter, OpenAIAdapter, OllamaAdapter
    Swap providers by changing configuration, no code changes needed.
    """
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: User prompt/message
            system: System prompt (instructions for the LLM)
            tools: List of available tools (MCP format)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
        
        Returns:
            LLMResponse with content and optional tool calls
        """
        pass
    
    @abstractmethod
    def parse_document(self, file_path: str) -> str:
        """
        Parse a document (PDF, markdown, etc.) into text.
        
        Args:
            file_path: Path to the document
        
        Returns:
            Extracted text content
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the name of the LLM provider (e.g., 'anthropic', 'openai')."""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Return the model being used (e.g., 'claude-sonnet-4', 'gpt-4')."""
        pass

