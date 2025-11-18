"""LiteLLM adapter with LangFuse integration for observability."""

from typing import List, Dict, Any, Optional
import os
from litellm import completion, Router
from langfuse import Langfuse
from langfuse.decorators import observe, langfuse_context

from interfaces.llm_provider import LLMProvider, LLMResponse, ToolCall


class LiteLLMAdapter(LLMProvider):
    """
    LiteLLM adapter with LangFuse observability.
    
    Features:
    - Unified API for 100+ LLM providers
    - Automatic fallbacks and retries
    - LangFuse tracing and prompt management
    - Cost tracking across providers
    """
    
    def __init__(
        self,
        model: str = "claude-sonnet",
        config_path: Optional[str] = None,
        enable_langfuse: bool = True
    ):
        """
        Initialize LiteLLM adapter.
        
        Args:
            model: Model name from litellm_config.yaml
            config_path: Path to litellm_config.yaml (optional)
            enable_langfuse: Enable LangFuse tracing
        """
        self.model = model
        self.enable_langfuse = enable_langfuse
        
        # Initialize LangFuse if enabled
        if self.enable_langfuse:
            self.langfuse = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            )
        
        # Initialize LiteLLM Router (if config provided)
        self.router = None
        if config_path:
            # Router enables fallbacks, load balancing, etc.
            self.router = Router(config_path=config_path)
    
    @observe(name="llm_generate", capture_input=True, capture_output=True)
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Generate response using LiteLLM with LangFuse tracing.
        
        Args:
            prompt: User prompt
            system: System prompt
            tools: Available tools (MCP format)
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            metadata: Additional metadata for LangFuse (e.g., user_id, session_id)
        
        Returns:
            LLMResponse with content and optional tool calls
        """
        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Add metadata to LangFuse trace
        if self.enable_langfuse and metadata:
            langfuse_context.update_current_trace(
                user_id=metadata.get("user_id"),
                session_id=metadata.get("session_id"),
                tags=metadata.get("tags", []),
                metadata=metadata
            )
        
        try:
            # Call LiteLLM (automatically traces to LangFuse if configured)
            if self.router:
                # Use router for fallbacks
                response = self.router.completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    tools=tools if tools else None
                )
            else:
                # Direct completion
                response = completion(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    tools=tools if tools else None
                )
            
            # Extract content and tool calls
            message = response.choices[0].message
            content = message.content or ""
            
            # Parse tool calls if present
            tool_calls = []
            if hasattr(message, "tool_calls") and message.tool_calls:
                for tc in message.tool_calls:
                    tool_calls.append(ToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=tc.function.arguments
                    ))
            
            # Extract usage
            usage = {}
            if hasattr(response, "usage"):
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            
            return LLMResponse(
                content=content,
                tool_calls=tool_calls,
                stop_reason=response.choices[0].finish_reason,
                usage=usage
            )
        
        except Exception as e:
            # Log error to LangFuse
            if self.enable_langfuse:
                langfuse_context.update_current_observation(
                    level="ERROR",
                    status_message=str(e)
                )
            raise
    
    def parse_document(self, file_path: str) -> str:
        """
        Parse a document into text.
        
        For PDFs, use pypdf2. For markdown, read directly.
        """
        if file_path.endswith(".pdf"):
            import PyPDF2
            text = ""
            with open(file_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
            return text
        elif file_path.endswith(".md"):
            with open(file_path, "r") as file:
                return file.read()
        else:
            # Generic text file
            with open(file_path, "r") as file:
                return file.read()
    
    @observe(name="get_prompt_from_langfuse")
    def get_prompt(self, prompt_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a prompt from LangFuse prompt management.
        
        Args:
            prompt_name: Name of the prompt in LangFuse
            variables: Variables to interpolate into the prompt
        
        Returns:
            Compiled prompt string
        """
        if not self.enable_langfuse:
            raise ValueError("LangFuse is not enabled")
        
        # Fetch prompt from LangFuse
        prompt = self.langfuse.get_prompt(prompt_name)
        
        # Compile with variables if provided
        if variables:
            return prompt.compile(**variables)
        return prompt.prompt
    
    def get_provider_name(self) -> str:
        """Return 'litellm' as the provider name."""
        return "litellm"
    
    def get_model_name(self) -> str:
        """Return the configured model name."""
        return self.model
    
    def flush_langfuse(self):
        """Flush LangFuse traces (call at end of session)."""
        if self.enable_langfuse:
            self.langfuse.flush()

