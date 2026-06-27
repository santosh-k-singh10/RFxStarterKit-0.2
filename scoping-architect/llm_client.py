"""
llm_client.py — LLM client configuration for IBM Services Essentials (OpenAI-compatible API).

Loads configuration from the main .env file (rfp-analyzer/.env) and provides a unified interface for LLM calls.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Optional, Any, cast
from dotenv import load_dotenv

# Load environment variables from the common .env file
common_env_path = Path(__file__).parent.parent / "common" / ".env"
if common_env_path.exists():
    load_dotenv(common_env_path)
    logging.info(f"Loaded environment from: {common_env_path}")
else:
    # Fallback to local .env if common one doesn't exist
    load_dotenv()
    logging.warning(f"Common .env not found at {common_env_path}, using local .env")

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified LLM client that uses IBM Services Essentials (OpenAI-compatible API).
    Falls back to direct Anthropic API if configured.
    """
    
    def __init__(self):
        self.api_base = os.getenv("OPENAI_API_BASE")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model_id = os.getenv("MODEL_ID")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Determine which client to use
        self.use_openai_compatible = bool(self.api_base and self.api_key and self.model_id)
        self.use_anthropic = bool(self.anthropic_key)
        
        if not self.use_openai_compatible and not self.use_anthropic:
            logger.warning(
                "No LLM configuration found. Set either:\n"
                "  - OPENAI_API_BASE, OPENAI_API_KEY, MODEL_ID (for IBM Services Essentials)\n"
                "  - ANTHROPIC_API_KEY (for direct Anthropic API)"
            )
    
    def is_configured(self) -> bool:
        """Check if LLM client is properly configured."""
        return self.use_openai_compatible or self.use_anthropic
    
    async def create_message(
        self,
        messages: list[dict[str, Any]],
        system: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """
        Create a message using the configured LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            system: Optional system prompt
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            
        Returns:
            Response dict with 'content' field containing the text response
        """
        logger.info("LLM create_message called")
        logger.info(f"  - Messages: {len(messages)}")
        logger.info(f"  - System prompt: {'Yes' if system else 'No'} ({len(system) if system else 0} chars)")
        logger.info(f"  - Max tokens: {max_tokens}")
        logger.info(f"  - Temperature: {temperature}")
        
        if self.use_openai_compatible:
            logger.info("  - Using: IBM Services Essentials (OpenAI-compatible)")
            return await self._create_with_openai_compatible(
                messages, system, max_tokens, temperature
            )
        elif self.use_anthropic:
            logger.info("  - Using: Anthropic Direct API")
            return await self._create_with_anthropic(
                messages, system, max_tokens, temperature
            )
        else:
            logger.error("LLM client not configured")
            raise RuntimeError("LLM client not configured. Check your .env file.")
    
    async def _create_with_openai_compatible(
        self,
        messages: list[dict[str, Any]],
        system: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        """Use OpenAI-compatible API (IBM Services Essentials)."""
        try:
            from openai import AsyncOpenAI
        except ImportError:
            raise ImportError(
                "openai package required for IBM Services Essentials. "
                "Install: pip install openai"
            )
        
        client = AsyncOpenAI(
            base_url=self.api_base,
            api_key=self.api_key,
        )
        
        # Add system message if provided
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend(messages)
        
        logger.info("Calling IBM Services Essentials API")
        logger.info(f"  - Model: {self.model_id}")
        logger.info(f"  - Base URL: {self.api_base}")
        logger.info(f"  - Total messages: {len(formatted_messages)}")
        
        model_id = self.model_id
        if not model_id:
            raise RuntimeError("MODEL_ID is not configured for OpenAI-compatible client.")
        
        response = await client.chat.completions.create(
            model=model_id,
            messages=cast(Any, formatted_messages),
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        content = response.choices[0].message.content or ""
        usage = response.usage
        
        logger.info("IBM Services Essentials response received")
        logger.info(f"  - Input tokens: {usage.prompt_tokens if usage else 'N/A'}")
        logger.info(f"  - Output tokens: {usage.completion_tokens if usage else 'N/A'}")
        logger.info(f"  - Response length: {len(content)} chars")
        
        return {
            "content": [{"type": "text", "text": content}],
            "model": model_id,
            "usage": {
                "input_tokens": usage.prompt_tokens if usage else None,
                "output_tokens": usage.completion_tokens if usage else None,
            },
        }
    
    async def _create_with_anthropic(
        self,
        messages: list[dict[str, Any]],
        system: Optional[str],
        max_tokens: int,
        temperature: float,
    ) -> dict[str, Any]:
        """Use direct Anthropic API."""
        try:
            from anthropic import AsyncAnthropic
        except ImportError:
            raise ImportError(
                "anthropic package required. Install: pip install anthropic"
            )
        
        client = AsyncAnthropic(api_key=self.anthropic_key)
        
        logger.info("Calling Anthropic API directly")
        logger.info(f"  - Model: claude-sonnet-4-20250514")
        logger.info(f"  - Messages: {len(messages)}")
        
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "",
            messages=cast(Any, messages),
        )
        
        logger.info("Anthropic response received")
        logger.info(f"  - Input tokens: {response.usage.input_tokens}")
        logger.info(f"  - Output tokens: {response.usage.output_tokens}")
        logger.info(f"  - Model used: {response.model}")
        
        return {
            "content": response.content,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
        }


# Global client instance
llm_client = LLMClient()