"""
Arize Phoenix Observability Module

This module provides OpenTelemetry-based observability for the RFP Analyzer,
integrating with Arize Phoenix for traces, metrics, and logs.

Usage:
    from observability import init_observability, trace_agent, trace_llm_call
    
    # Initialize at application startup
    init_observability()
    
    # Use decorators for tracing
    @trace_agent("functional_extraction")
    def extract_functional(state):
        ...
    
    @trace_llm_call()
    def call_claude(prompt):
        ...
"""

from .phoenix_tracer import (
    init_observability,
    shutdown_observability,
    get_tracer,
    get_meter,
)
from .decorators import (
    trace_agent,
    trace_llm_call,
    trace_operation,
)
from .metrics import (
    record_analysis_started,
    record_analysis_completed,
    record_analysis_failed,
    record_requirements_extracted,
    record_llm_call,
    record_token_usage,
)
from .config import ObservabilityConfig

__all__ = [
    # Initialization
    "init_observability",
    "shutdown_observability",
    "get_tracer",
    "get_meter",
    # Decorators
    "trace_agent",
    "trace_llm_call",
    "trace_operation",
    # Metrics
    "record_analysis_started",
    "record_analysis_completed",
    "record_analysis_failed",
    "record_requirements_extracted",
    "record_llm_call",
    "record_token_usage",
    # Configuration
    "ObservabilityConfig",
]

__version__ = "1.0.0"

# Made with Bob
