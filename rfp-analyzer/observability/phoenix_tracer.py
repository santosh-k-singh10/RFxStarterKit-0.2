"""
Phoenix Tracer - OpenTelemetry Setup

Initializes and manages OpenTelemetry instrumentation for Arize Phoenix.
"""

import logging
from typing import Optional
from contextlib import contextmanager

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter

from .config import get_config

logger = logging.getLogger(__name__)

# Global state
_tracer_provider: Optional[TracerProvider] = None
_meter_provider: Optional[MeterProvider] = None
_initialized: bool = False


def init_observability() -> bool:
    """
    Initialize OpenTelemetry instrumentation with Arize Phoenix.
    
    Returns:
        bool: True if initialization succeeded, False otherwise
    """
    global _tracer_provider, _meter_provider, _initialized
    
    if _initialized:
        logger.warning("Observability already initialized")
        return True
    
    config = get_config()
    
    if not config.is_enabled:
        logger.info("Observability is disabled")
        return False
    
    try:
        # Create resource with service information
        resource = Resource.create(config.get_resource_attributes())
        
        # Initialize Tracer Provider
        if config.trace_agents or config.trace_llm_calls or config.trace_context_studio:
            _tracer_provider = TracerProvider(resource=resource)
            
            # Create OTLP span exporter with HTTP transport
            # IMPORTANT: Agent Studio proxy requires 'api_key' header, not 'Authorization'
            headers = {"Content-Type": "application/x-protobuf"}
            if config.phoenix_api_key:
                headers["api_key"] = config.phoenix_api_key
            
            span_exporter = OTLPSpanExporter(
                endpoint=config.phoenix_endpoint,  # Use base endpoint, not otlp_endpoint
                headers=headers,
                timeout=config.export_timeout,
            )
            
            # Add batch span processor
            span_processor = BatchSpanProcessor(
                span_exporter,
                max_queue_size=config.max_queue_size,
                max_export_batch_size=config.batch_size,
            )
            _tracer_provider.add_span_processor(span_processor)
            
            # Set global tracer provider
            trace.set_tracer_provider(_tracer_provider)
            logger.info("Trace provider initialized successfully")
        
        # Initialize Meter Provider
        if config.collect_metrics:
            # Create OTLP metric exporter
            metric_exporter = OTLPMetricExporter(
                endpoint=config.phoenix_endpoint + "/v1/metrics",
                headers=config.auth_headers,
                timeout=config.export_timeout,
            )
            
            # Create periodic metric reader
            metric_reader = PeriodicExportingMetricReader(
                metric_exporter,
                export_interval_millis=config.metric_export_interval * 1000,
            )
            
            _meter_provider = MeterProvider(
                resource=resource,
                metric_readers=[metric_reader],
            )
            
            # Set global meter provider
            metrics.set_meter_provider(_meter_provider)
            logger.info("Meter provider initialized successfully")
        
        _initialized = True
        logger.info(
            f"Observability initialized successfully for project '{config.project_name}' "
            f"in environment '{config.environment}'"
        )
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize observability: {e}", exc_info=True)
        return False


def shutdown_observability() -> None:
    """Shutdown observability and flush all pending telemetry."""
    global _tracer_provider, _meter_provider, _initialized
    
    if not _initialized:
        return
    
    try:
        if _tracer_provider:
            _tracer_provider.shutdown()
            logger.info("Tracer provider shut down successfully")
        
        if _meter_provider:
            _meter_provider.shutdown()
            logger.info("Meter provider shut down successfully")
        
        _initialized = False
        _tracer_provider = None
        _meter_provider = None
        
    except Exception as e:
        logger.error(f"Error during observability shutdown: {e}", exc_info=True)


def get_tracer(name: str = "rfp-analyzer") -> trace.Tracer:
    """
    Get a tracer instance.
    
    Args:
        name: Name of the tracer (typically module or component name)
    
    Returns:
        Tracer instance
    """
    if not _initialized:
        logger.warning("Observability not initialized, returning no-op tracer")
    
    return trace.get_tracer(name)


def get_meter(name: str = "rfp-analyzer") -> metrics.Meter:
    """
    Get a meter instance.
    
    Args:
        name: Name of the meter (typically module or component name)
    
    Returns:
        Meter instance
    """
    if not _initialized:
        logger.warning("Observability not initialized, returning no-op meter")
    
    return metrics.get_meter(name)


@contextmanager
def observability_context():
    """
    Context manager for observability lifecycle.
    
    Usage:
        with observability_context():
            # Your code here
            pass
    """
    try:
        init_observability()
        yield
    finally:
        shutdown_observability()


def is_initialized() -> bool:
    """Check if observability is initialized."""
    return _initialized


def get_current_span() -> Optional[trace.Span]:
    """Get the current active span, if any."""
    return trace.get_current_span()


def add_span_attribute(key: str, value) -> None:
    """
    Add an attribute to the current span.
    
    Args:
        key: Attribute key
        value: Attribute value
    """
    span = get_current_span()
    if span and span.is_recording():
        span.set_attribute(key, value)


def add_span_event(name: str, attributes: Optional[dict] = None) -> None:
    """
    Add an event to the current span.
    
    Args:
        name: Event name
        attributes: Optional event attributes
    """
    span = get_current_span()
    if span and span.is_recording():
        span.add_event(name, attributes=attributes or {})


def record_exception(exception: Exception) -> None:
    """
    Record an exception in the current span.
    
    Args:
        exception: The exception to record
    """
    span = get_current_span()
    if span and span.is_recording():
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))

# Made with Bob
