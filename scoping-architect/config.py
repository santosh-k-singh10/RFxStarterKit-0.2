"""
config.py — Configuration management for RFP Analyzer.

Loads all settings from .env file.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # LLM Configuration
    OPENAI_API_BASE: str = os.getenv("OPENAI_API_BASE", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    MODEL_ID: str = os.getenv("MODEL_ID", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "*")
    
    # MCP Configuration (if needed)
    MCP_BASE_URL: str = os.getenv("MCP_BASE_URL", "")
    MCP_SERVER_ID: str = os.getenv("MCP_SERVER_ID", "")
    MCP_ACCESS_TOKEN: str = os.getenv("MCP_ACCESS_TOKEN", "")
    
    @classmethod
    def is_llm_configured(cls) -> bool:
        """Check if LLM is properly configured."""
        return bool(
            (cls.OPENAI_API_BASE and cls.OPENAI_API_KEY and cls.MODEL_ID)
            or cls.ANTHROPIC_API_KEY
        )
    
    @classmethod
    def get_llm_type(cls) -> str:
        """Get the configured LLM type."""
        if cls.OPENAI_API_BASE and cls.OPENAI_API_KEY and cls.MODEL_ID:
            return "IBM Services Essentials (OpenAI-compatible)"
        elif cls.ANTHROPIC_API_KEY:
            return "Anthropic Direct API"
        return "Not configured"


config = Config()