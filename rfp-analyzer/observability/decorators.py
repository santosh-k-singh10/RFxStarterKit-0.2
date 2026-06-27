"""
Tracing Decorators

Provides decorators for automatic tracing of agents, LLM calls, and operations.
"""

import functools
import time
import logging
from typing import Callable, Optional, Any

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .config import get_config
from .phoenix_tracer import get_tracer, record_exception

logger = logging.getLogger(__name__)


def trace_agent(agent_name: str, extract_requirements: bool = True):
    """
    Decorator to trace agent execution.
    
    Args:
        agent_name: Name of the agent (e.g., "functional_extraction")
        extract_requirements: Whether to extract requirement count from result
    
    Usage:
        @trace_agent("functional_extraction")
        def extract_functional(state):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            
            # Skip tracing if disabled
            if not config.is_enabled or not config.trace_agents:
                return func(*args, **kwargs)
            
            tracer = get_tracer(__name__)
            
            with tracer.start_as_current_span(
                f"agent.{agent_name}",
                kind=trace.SpanKind.INTERNAL,
            ) as span:
                # Add agent metadata
                span.set_attribute("agent.name", agent_name)
                span.set_attribute("agent.type", "extraction")
                
                start_time = time.time()
                
                try:
                    # Execute the agent
                    result = func(*args, **kwargs)
                    
                    # Calculate duration
                    duration = time.time() - start_time
                    span.set_attribute("agent.duration_ms", int(duration * 1000))
                    
                    # Extract requirement count if enabled
                    if extract_requirements and result:
                        if isinstance(result, dict):
                            # Handle state dict
                            req_count = len(result.get("requirements", []))
                            span.set_attribute("agent.requirements_extracted", req_count)
                        elif hasattr(result, "requirements"):
                            # Handle state object
                            req_count = len(result.requirements)
                            span.set_attribute("agent.requirements_extracted", req_count)
                    
                    # Mark as successful
                    span.set_status(Status(StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Record the exception
                    record_exception(e)
                    span.set_attribute("agent.error", str(e))
                    logger.error(f"Agent {agent_name} failed: {e}", exc_info=True)
                    raise
        
        return wrapper
    return decorator


def trace_llm_call(provider: str = "anthropic", model: Optional[str] = None):
    """
    Decorator to trace LLM API calls.
    
    Args:
        provider: LLM provider name (e.g., "anthropic", "openai")
        model: Model name (e.g., "claude-3-5-sonnet-20241022")
    
    Usage:
        @trace_llm_call(provider="anthropic", model="claude-3-5-sonnet")
        def call_claude(prompt, **kwargs):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            
            # Skip tracing if disabled
            if not config.is_enabled or not config.trace_llm_calls:
                return func(*args, **kwargs)
            
            tracer = get_tracer(__name__)
            
            with tracer.start_as_current_span(
                f"llm.{provider}.call",
                kind=trace.SpanKind.CLIENT,
            ) as span:
                # Add LLM metadata
                span.set_attribute("llm.provider", provider)
                if model:
                    span.set_attribute("llm.model", model)
                
                # Extract model from kwargs if not provided
                if not model and "model" in kwargs:
                    span.set_attribute("llm.model", kwargs["model"])
                
                # Add request metadata
                if "max_tokens" in kwargs:
                    span.set_attribute("llm.max_tokens", kwargs["max_tokens"])
                if "temperature" in kwargs:
                    span.set_attribute("llm.temperature", kwargs["temperature"])
                
                start_time = time.time()
                
                try:
                    # Execute the LLM call
                    result = func(*args, **kwargs)
                    
                    # Calculate latency
                    latency = time.time() - start_time
                    span.set_attribute("llm.latency_ms", int(latency * 1000))
                    
                    # Extract token usage if available
                    if hasattr(result, "usage"):
                        usage = result.usage
                        if hasattr(usage, "input_tokens"):
                            span.set_attribute("llm.tokens.prompt", usage.input_tokens)
                        if hasattr(usage, "output_tokens"):
                            span.set_attribute("llm.tokens.completion", usage.output_tokens)
                        
                        # Calculate total tokens
                        total_tokens = getattr(usage, "input_tokens", 0) + getattr(usage, "output_tokens", 0)
                        span.set_attribute("llm.tokens.total", total_tokens)
                    
                    # Mark as successful
                    span.set_status(Status(StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Record the exception
                    record_exception(e)
                    span.set_attribute("llm.error", str(e))
                    
                    # Check for rate limiting
                    if "rate" in str(e).lower() or "429" in str(e):
                        span.set_attribute("llm.rate_limited", True)
                    
                    logger.error(f"LLM call to {provider} failed: {e}", exc_info=True)
                    raise
        
        return wrapper
    return decorator


def trace_operation(operation_name: str, operation_type: str = "internal"):
    """
    Decorator to trace generic operations.
    
    Args:
        operation_name: Name of the operation (e.g., "document_parsing", "synthesis")
        operation_type: Type of operation (e.g., "internal", "io", "computation")
    
    Usage:
        @trace_operation("document_parsing", "io")
        def parse_document(file_path):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            
            # Skip tracing if disabled
            if not config.is_enabled:
                return func(*args, **kwargs)
            
            tracer = get_tracer(__name__)
            
            with tracer.start_as_current_span(
                f"operation.{operation_name}",
                kind=trace.SpanKind.INTERNAL,
            ) as span:
                # Add operation metadata
                span.set_attribute("operation.name", operation_name)
                span.set_attribute("operation.type", operation_type)
                
                start_time = time.time()
                
                try:
                    # Execute the operation
                    result = func(*args, **kwargs)
                    
                    # Calculate duration
                    duration = time.time() - start_time
                    span.set_attribute("operation.duration_ms", int(duration * 1000))
                    
                    # Mark as successful
                    span.set_status(Status(StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Record the exception
                    record_exception(e)
                    span.set_attribute("operation.error", str(e))
                    logger.error(f"Operation {operation_name} failed: {e}", exc_info=True)
                    raise
        
        return wrapper
    return decorator


def trace_context_studio_query(query_type: str = "vector"):
    """
    Decorator to trace Context Studio queries.
    
    Args:
        query_type: Type of query (e.g., "vector", "keyword", "hybrid")
    
    Usage:
        @trace_context_studio_query("vector")
        def vector_query(query, top_k=5):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            
            # Skip tracing if disabled
            if not config.is_enabled or not config.trace_context_studio:
                return func(*args, **kwargs)
            
            tracer = get_tracer(__name__)
            
            with tracer.start_as_current_span(
                f"context_studio.{query_type}_query",
                kind=trace.SpanKind.CLIENT,
            ) as span:
                # Add query metadata
                span.set_attribute("context_studio.query_type", query_type)
                
                if "top_k" in kwargs:
                    span.set_attribute("context_studio.top_k", kwargs["top_k"])
                
                start_time = time.time()
                
                try:
                    # Execute the query
                    result = func(*args, **kwargs)
                    
                    # Calculate latency
                    latency = time.time() - start_time
                    span.set_attribute("context_studio.latency_ms", int(latency * 1000))
                    
                    # Extract result count
                    if isinstance(result, list):
                        span.set_attribute("context_studio.results_count", len(result))
                    
                    # Mark as successful
                    span.set_status(Status(StatusCode.OK))
                    
                    return result
                    
                except Exception as e:
                    # Record the exception
                    record_exception(e)
                    span.set_attribute("context_studio.error", str(e))
                    logger.error(f"Context Studio {query_type} query failed: {e}", exc_info=True)
                    raise
        
        return wrapper
    return decorator

# Made with Bob
