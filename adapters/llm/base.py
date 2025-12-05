"""Base LLM interface for adapters."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class BaseLLM(ABC):
    """Base class for LLM adapters."""
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        **kwargs
    ) -> Any:
        """Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system: System prompt (optional)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional model-specific parameters
            
        Returns:
            Response object with content
        """
        pass
    
    def filter_providers(self, rules: str, candidates: list, patient: dict, appointment: dict) -> list:
        """Filter providers based on rules (for mock compatibility).
        
        This is a convenience method for mock implementations.
        Real LLMs should use generate() with appropriate prompts.
        """
        # Default implementation: return all candidates
        return [c.get("provider_id") for c in candidates if c]
    
    def score_providers(self, rules: str, providers: list, patient: dict, appointment: dict) -> dict:
        """Score providers based on rules (for mock compatibility).
        
        This is a convenience method for mock implementations.
        Real LLMs should use generate() with appropriate prompts.
        """
        # Default implementation: return equal scores
        return {p.get("provider_id"): 50 for p in providers if p}

