"""Pluggable adapter implementations.

For mock-first development, import adapters directly from their modules:
- from adapters.llm.mock_llm import MockLLM
- from adapters.llm.litellm_adapter import LiteLLMAdapter (requires litellm package)
- from adapters.events.memory_queue import MemoryEventBus
"""

# Note: Not importing here to avoid dependency issues during mock-first development
# Import directly from submodules as needed

__all__ = []


