"""
phase0/llm_client.py
--------------------
Shared LLM client for Phase 0 that uses the same authentication pattern as RFP Analyzer.

Uses OpenAI-compatible API with IBM Services Essentials endpoint.
Falls back to direct Anthropic API if ANTHROPIC_API_KEY is set.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from common/.env
common_env_path = Path(__file__).parent.parent.parent.parent / "common" / ".env"
if common_env_path.exists():
    load_dotenv(common_env_path)
    logging.info(f"Loaded environment from: {common_env_path}")
else:
    # Fallback to default .env loading
    load_dotenv()
    logging.warning(f"Common .env not found at {common_env_path}, using default .env loading")

logger = logging.getLogger(__name__)


def get_anthropic_client():
    """
    Get an Anthropic client using the same authentication pattern as RFP Analyzer.
    
    Priority:
    1. OpenAI-compatible API (IBM Services Essentials) - converts to Anthropic format
    2. Direct Anthropic API - if ANTHROPIC_API_KEY is set
    
    Returns:
        anthropic.Anthropic client or OpenAICompatibleAnthropicClient
    """
    import anthropic
    
    # Check for OpenAI-compatible API configuration (IBM Services Essentials)
    openai_api_base = os.getenv("OPENAI_API_BASE")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    model_id = os.getenv("MODEL_ID")
    
    if openai_api_base and openai_api_key and model_id:
        logger.info("Using OpenAI-compatible API (IBM Services Essentials) for Phase 0")
        return OpenAICompatibleAnthropicClient(
            api_base=openai_api_base,
            api_key=openai_api_key,
            model_id=model_id
        )
    
    # Fall back to direct Anthropic API
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        logger.info("Using direct Anthropic API for Phase 0")
        return anthropic.Anthropic(api_key=anthropic_key)
    
    # No valid configuration found
    raise ValueError(
        "No LLM configuration found for Phase 0. Set either:\n"
        "  - OPENAI_API_BASE, OPENAI_API_KEY, MODEL_ID (for IBM Services Essentials)\n"
        "  - ANTHROPIC_API_KEY (for direct Anthropic API)"
    )


class OpenAICompatibleAnthropicClient:
    """
    Wrapper that makes OpenAI-compatible API look like Anthropic's client.
    
    This allows Phase 0 to use the same IBM Services Essentials endpoint
    as the RFP Analyzer without changing Phase 0's code structure.
    """
    
    def __init__(self, api_base: str, api_key: str, model_id: str):
        from openai import OpenAI
        
        self.openai_client = OpenAI(
            api_key=api_key,
            base_url=api_base,
            timeout=120.0
        )
        self.model_id = model_id
        self.messages = MessagesProxy(self.openai_client, self.model_id)
    
    def __repr__(self):
        return f"OpenAICompatibleAnthropicClient(model={self.model_id})"


class MessagesProxy:
    """
    Proxy for the messages.create() method that converts between
    OpenAI and Anthropic API formats.
    """
    
    def __init__(self, openai_client, model_id: str):
        self.openai_client = openai_client
        self.model_id = model_id
    
    def create(
        self,
        model: str,
        max_tokens: int,
        system: Optional[str] = None,
        messages: Optional[list] = None,
        temperature: float = 0.0,
        **kwargs
    ):
        """
        Create a message using OpenAI-compatible API but with Anthropic's interface.
        
        Args:
            model: Model identifier (ignored, uses self.model_id)
            max_tokens: Maximum tokens in response
            system: System prompt
            messages: List of message dicts
            temperature: Sampling temperature
            
        Returns:
            AnthropicCompatibleResponse object
        """
        # Convert Anthropic format to OpenAI format
        openai_messages = []
        
        # Add system message if provided
        if system:
            openai_messages.append({"role": "system", "content": system})
        
        # Add user/assistant messages
        if messages:
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                # Handle content that might be a list (Anthropic format)
                if isinstance(content, list):
                    # Extract text from content blocks
                    text_parts = []
                    for block in content:
                        if isinstance(block, dict) and block.get("type") == "text":
                            text_parts.append(block.get("text", ""))
                    content = "\n".join(text_parts)
                
                openai_messages.append({"role": role, "content": content})
        
        # Call OpenAI-compatible API
        response = self.openai_client.chat.completions.create(
            model=self.model_id,
            messages=openai_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        # Convert response to Anthropic format
        return AnthropicCompatibleResponse(response)


class AnthropicCompatibleResponse:
    """
    Wrapper that makes OpenAI response look like Anthropic's response.
    """
    
    def __init__(self, openai_response):
        self.openai_response = openai_response
        
        # Extract content
        content_text = openai_response.choices[0].message.content or ""
        
        # Create Anthropic-style content blocks
        self.content = [
            ContentBlock(text=content_text)
        ]
        
        # Usage information
        if openai_response.usage:
            self.usage = Usage(
                input_tokens=openai_response.usage.prompt_tokens,
                output_tokens=openai_response.usage.completion_tokens
            )
        else:
            self.usage = Usage(input_tokens=0, output_tokens=0)
    
    def __repr__(self):
        return f"AnthropicCompatibleResponse(content_blocks={len(self.content)})"


class ContentBlock:
    """Anthropic-style content block."""
    
    def __init__(self, text: str):
        self.text = text
        self.type = "text"
    
    def __repr__(self):
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"ContentBlock(text='{preview}')"


class Usage:
    """Anthropic-style usage information."""
    
    def __init__(self, input_tokens: int, output_tokens: int):
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens
    
    def __repr__(self):
        return f"Usage(input={self.input_tokens}, output={self.output_tokens})"

# Made with Bob
