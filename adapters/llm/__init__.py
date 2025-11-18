"""LLM adapters.

Available adapters:
- MockLLM: Hardcoded responses for testing (no dependencies)
- LiteLLMAdapter: Real LLM via LiteLLM (requires litellm package)

Import directly as needed:
  from adapters.llm.mock_llm import MockLLM
  from adapters.llm.litellm_adapter import LiteLLMAdapter
"""

# Note: Not importing here to avoid dependency issues during mock-first development

__all__ = []


