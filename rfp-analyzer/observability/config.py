"""
Observability Configuration

Manages configuration for Arize Phoenix observability integration.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class ObservabilityConfig(BaseSettings):
    """Configuration for observability features."""
    
    # Core Settings
    enabled: bool = Field(
        default=True,
        description="Master switch for all observability features"
    )
    
    phoenix_endpoint: str = Field(
        default="https://agentstudio.servicesessentials.ibm.com/api/proxy/observability",
        description="Arize Phoenix endpoint URL"
    )
    
    phoenix_api_key: Optional[str] = Field(
        default=None,
        description="Arize Phoenix API key for authentication"
    )
    
    project_name: str = Field(
        default="rfp-analyzer",
        description="Project name for Phoenix"
    )
    
    environment: str = Field(
        default="production",
        description="Environment name (development, staging, production)"
    )
    
    # Feature Flags
    trace_agents: bool = Field(
        default=True,
        description="Enable agent execution tracing"
    )
    
    trace_llm_calls: bool = Field(
        default=True,
        description="Enable LLM call tracing"
    )
    
    trace_context_studio: bool = Field(
        default=True,
        description="Enable Context Studio query tracing"
    )
    
    collect_metrics: bool = Field(
        default=True,
        description="Enable metrics collection"
    )
    
    collect_logs: bool = Field(
        default=True,
        description="Enable log collection"
    )
    
    # Sampling Configuration
    trace_sample_rate: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Trace sampling rate (0.0 to 1.0, where 1.0 = 100%)"
    )
    
    metric_export_interval: int = Field(
        default=60,
        ge=1,
        description="Metric export interval in seconds"
    )
    
    # Performance Tuning
    batch_size: int = Field(
        default=100,
        ge=1,
        description="Batch size for telemetry export"
    )
    
    export_timeout: int = Field(
        default=30,
        ge=1,
        description="Export timeout in seconds"
    )
    
    max_queue_size: int = Field(
        default=2048,
        ge=1,
        description="Maximum queue size for telemetry data"
    )
    
    class Config:
        env_prefix = "OBSERVABILITY_"
        case_sensitive = False
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from environment
    
    @property
    def is_enabled(self) -> bool:
        """Check if observability is enabled and properly configured."""
        return self.enabled and bool(self.phoenix_api_key)
    
    @property
    def otlp_endpoint(self) -> str:
        """Get the OTLP endpoint URL."""
        # Agent Studio proxy handles routing
        return self.phoenix_endpoint
    
    @property
    def auth_headers(self) -> dict:
        """Get authentication headers for Phoenix (Agent Studio format)."""
        headers = {"Content-Type": "application/x-protobuf"}
        if self.phoenix_api_key:
            # Agent Studio uses 'api_key' header, not 'Authorization'
            headers["api_key"] = self.phoenix_api_key
        return headers
    
    def get_resource_attributes(self) -> dict:
        """Get resource attributes for OpenTelemetry."""
        return {
            "service.name": self.project_name,
            "service.version": "1.0.0",
            "deployment.environment": self.environment,
        }


# Global configuration instance
_config: Optional[ObservabilityConfig] = None


def get_config() -> ObservabilityConfig:
    """Get the global observability configuration."""
    global _config
    if _config is None:
        _config = ObservabilityConfig()
    return _config


def reload_config() -> ObservabilityConfig:
    """Reload the configuration from environment."""
    global _config
    _config = ObservabilityConfig()
    return _config

# Made with Bob
