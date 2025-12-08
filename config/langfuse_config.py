"""LangFuse Configuration and Prompt Management.

This module provides:
1. Environment-based configuration
2. Prompt loading from LangFuse
3. Prompt versioning and caching
4. Fallback to local prompts if LangFuse unavailable
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class PromptConfig:
    """Configuration for a single prompt."""
    name: str
    version: int
    fallback_template: Optional[str] = None


class LangFuseConfig:
    """LangFuse configuration and prompt management."""
    
    # Prompt names - Only 2 prompts used in the system
    ORCHESTRATOR_TEMPLATE = "healthcare-orchestrator-template"
    PATIENT_ENGAGEMENT = "patient-engagement-message"
    
    # Default to production label
    PROMPT_LABEL = os.getenv("LANGFUSE_PROMPT_LABEL", "production")
    
    # LangFuse credentials
    PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
    SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
    HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
    
    # Feature flags
    ENABLED = os.getenv("LANGFUSE_ENABLED", "true").lower() == "true"
    
    @classmethod
    def is_configured(cls) -> bool:
        """Check if LangFuse is properly configured."""
        return bool(cls.PUBLIC_KEY and cls.SECRET_KEY and cls.ENABLED)
    
    @classmethod
    def get_prompt_name(cls, prompt_type: str) -> str:
        """Get prompt name for a given type."""
        prompt_map = {
            "orchestrator": cls.ORCHESTRATOR_TEMPLATE,
            "patient_engagement": cls.PATIENT_ENGAGEMENT,
        }
        return prompt_map.get(prompt_type, "")


class PromptManager:
    """Manages prompt loading and caching."""
    
    def __init__(self):
        """Initialize prompt manager."""
        self.langfuse_client = None
        self._init_langfuse()
    
    def _init_langfuse(self):
        """Initialize LangFuse client if configured."""
        if LangFuseConfig.is_configured():
            try:
                from langfuse import Langfuse
                self.langfuse_client = Langfuse(
                    public_key=LangFuseConfig.PUBLIC_KEY,
                    secret_key=LangFuseConfig.SECRET_KEY,
                    host=LangFuseConfig.HOST
                )
                print(f"✅ LangFuse initialized: {LangFuseConfig.HOST}")
            except ImportError:
                print("⚠️  LangFuse not installed. Install: pip install langfuse")
            except Exception as e:
                print(f"⚠️  LangFuse initialization failed: {e}")
    
    @lru_cache(maxsize=32)
    def get_prompt(self, prompt_name: str, label: str = None) -> Dict[str, Any]:
        """Get prompt from LangFuse with caching.
        
        Args:
            prompt_name: Name of the prompt (e.g., "healthcare-chat-router")
            label: Label to fetch (e.g., "production", "staging"). Defaults to "production"
        
        Returns:
            Prompt configuration dict
        """
        if label is None:
            label = LangFuseConfig.PROMPT_LABEL
        
        if self.langfuse_client:
            try:
                # Get prompt with specific label (e.g., production)
                prompt = self.langfuse_client.get_prompt(prompt_name, label=label)
                return {
                    "name": prompt_name,
                    "system": prompt.prompt,
                    "version": prompt.version,
                    "label": label,
                    "config": prompt.config if hasattr(prompt, 'config') else {},
                }
            except Exception as e:
                print(f"❌ Failed to load prompt {prompt_name} (label: {label}) from LangFuse: {e}")
                raise Exception(f"LangFuse prompt '{prompt_name}' not found. Please check LangFuse configuration.")


# Global instance
prompt_manager = PromptManager()


def get_prompt(prompt_type: str, label: str = None) -> Dict[str, Any]:
    """Convenience function to get a prompt by type.
    
    Args:
        prompt_type: Type of prompt (orchestrator, patient_engagement)
        label: Label to fetch (e.g., "production", "staging"). Defaults to "production"
    
    Returns:
        Prompt configuration with system prompt, version, and label
    """
    prompt_name = LangFuseConfig.get_prompt_name(prompt_type)
    if label is None:
        label = LangFuseConfig.PROMPT_LABEL
    return prompt_manager.get_prompt(prompt_name, label=label)


if __name__ == "__main__":
    # Test configuration
    print("\n" + "=" * 60)
    print("LangFuse Configuration Test")
    print("=" * 60)
    
    print(f"\nLangFuse Enabled: {LangFuseConfig.ENABLED}")
    print(f"LangFuse Configured: {LangFuseConfig.is_configured()}")
    print(f"Host: {LangFuseConfig.HOST}")
    
    print(f"\nPrompt Names (LangFuse-only, no local fallbacks):")
    print(f"  Orchestrator: {LangFuseConfig.ORCHESTRATOR_TEMPLATE}")
    print(f"  Patient Engagement: {LangFuseConfig.PATIENT_ENGAGEMENT}")
    print(f"\nDefault Label: {LangFuseConfig.PROMPT_LABEL}")
    
    print(f"\nTesting prompt loading...")
    prompt = get_prompt("chat_router", label="production")
    print(f"  Loaded: {prompt['name']}")
    print(f"  Version: {prompt.get('version', 'N/A')}")
    print(f"  Label: {prompt.get('label', 'N/A')}")
    
    print("\n" + "=" * 60)

