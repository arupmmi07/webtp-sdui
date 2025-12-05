"""
LLM Settings Configuration

Centralized configuration for all LLM-related settings.
Override these by setting environment variables.
"""

import os
from pathlib import Path

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[CONFIG] Loaded .env from {env_path}")
except ImportError:
    print("[CONFIG] Warning: python-dotenv not installed. Run: pip install python-dotenv")
except Exception as e:
    print(f"[CONFIG] Warning: Could not load .env: {e}")


class LLMSettings:
    """LLM configuration settings."""
    
    # ============================================================
    # Timeout Settings
    # ============================================================
    
    # Request timeout in seconds (how long to wait for LLM response)
    REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "120"))  # 2 minutes default
    
    # Connection timeout in seconds
    CONNECTION_TIMEOUT = int(os.getenv("LLM_CONNECTION_TIMEOUT", "30"))  # 30 seconds
    
    
    # ============================================================
    # Token Settings
    # ============================================================
    
    # Maximum tokens for template-driven orchestrator
    ORCHESTRATOR_MAX_TOKENS = int(os.getenv("LLM_ORCHESTRATOR_MAX_TOKENS", "4000"))
    
    # Maximum tokens for smart scheduling agent
    SCHEDULING_MAX_TOKENS = int(os.getenv("LLM_SCHEDULING_MAX_TOKENS", "2000"))
    
    # Maximum tokens for patient engagement
    ENGAGEMENT_MAX_TOKENS = int(os.getenv("LLM_ENGAGEMENT_MAX_TOKENS", "1000"))
    
    
    # ============================================================
    # Temperature Settings (0.0 = deterministic, 1.0 = creative)
    # ============================================================
    
    # Temperature for orchestrator (decision-making)
    ORCHESTRATOR_TEMPERATURE = float(os.getenv("LLM_ORCHESTRATOR_TEMPERATURE", "0.3"))
    
    # Temperature for scheduling (matching logic)
    SCHEDULING_TEMPERATURE = float(os.getenv("LLM_SCHEDULING_TEMPERATURE", "0.2"))
    
    # Temperature for patient messages (more creative)
    ENGAGEMENT_TEMPERATURE = float(os.getenv("LLM_ENGAGEMENT_TEMPERATURE", "0.7"))
    
    
    # ============================================================
    # Retry Settings
    # ============================================================
    
    # Number of retries on failure
    MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
    
    # Retry delay in seconds
    RETRY_DELAY = int(os.getenv("LLM_RETRY_DELAY", "2"))
    
    
    # ============================================================
    # Model Settings
    # ============================================================
    
    # Default model for orchestrator
    ORCHESTRATOR_MODEL = os.getenv("LITELLM_DEFAULT_MODEL", "openai/gpt-oss-20b")
    
    # LiteLLM base URL
    LITELLM_BASE_URL = os.getenv("LITELLM_BASE_URL", "http://localhost:1234/v1")
    
    # LiteLLM API key
    LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "sk-1234")
    
    
    # ============================================================
    # Fallback Settings
    # ============================================================
    
    # Enable automatic fallback to rule-based on LLM failure
    ENABLE_FALLBACK = os.getenv("LLM_ENABLE_FALLBACK", "true").lower() == "true"
    
    # Threshold score for auto-assignment (0-100)
    AUTO_ASSIGN_THRESHOLD = int(os.getenv("LLM_AUTO_ASSIGN_THRESHOLD", "60"))
    
    
    # ============================================================
    # Debug Settings
    # ============================================================
    
    # Enable debug logging
    DEBUG = os.getenv("LLM_DEBUG", "false").lower() == "true"
    
    # Log prompts and responses
    LOG_PROMPTS = os.getenv("LLM_LOG_PROMPTS", "false").lower() == "true"
    
    
    @classmethod
    def get_all_settings(cls) -> dict:
        """Get all settings as a dictionary."""
        return {
            "timeouts": {
                "request_timeout": cls.REQUEST_TIMEOUT,
                "connection_timeout": cls.CONNECTION_TIMEOUT,
            },
            "tokens": {
                "orchestrator_max_tokens": cls.ORCHESTRATOR_MAX_TOKENS,
                "scheduling_max_tokens": cls.SCHEDULING_MAX_TOKENS,
                "engagement_max_tokens": cls.ENGAGEMENT_MAX_TOKENS,
            },
            "temperature": {
                "orchestrator": cls.ORCHESTRATOR_TEMPERATURE,
                "scheduling": cls.SCHEDULING_TEMPERATURE,
                "engagement": cls.ENGAGEMENT_TEMPERATURE,
            },
            "retry": {
                "max_retries": cls.MAX_RETRIES,
                "retry_delay": cls.RETRY_DELAY,
            },
            "model": {
                "orchestrator_model": cls.ORCHESTRATOR_MODEL,
                "litellm_base_url": cls.LITELLM_BASE_URL,
            },
            "fallback": {
                "enable_fallback": cls.ENABLE_FALLBACK,
                "auto_assign_threshold": cls.AUTO_ASSIGN_THRESHOLD,
            },
            "debug": {
                "debug": cls.DEBUG,
                "log_prompts": cls.LOG_PROMPTS,
            }
        }
    
    @classmethod
    def print_settings(cls):
        """Print all current settings."""
        import json
        print("\n" + "="*60)
        print("LLM CONFIGURATION SETTINGS")
        print("="*60)
        print(json.dumps(cls.get_all_settings(), indent=2))
        print("="*60 + "\n")


# Singleton instance
settings = LLMSettings()

