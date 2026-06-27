"""
Metrics Collection

Provides functions for recording metrics to Arize Phoenix.
"""

import logging
from typing import Optional

from opentelemetry import metrics

from .config import get_config
from .phoenix_tracer import get_meter

logger = logging.getLogger(__name__)

# Global metric instruments
_analysis_counter: Optional[metrics.Counter] = None
_requirements_counter: Optional[metrics.Counter] = None
_llm_call_counter: Optional[metrics.Counter] = None
_token_counter: Optional[metrics.Counter] = None
_duration_histogram: Optional[metrics.Histogram] = None
_latency_histogram: Optional[metrics.Histogram] = None
_active_analyses_gauge: Optional[metrics.UpDownCounter] = None


def _init_metrics():
    """Initialize metric instruments."""
    global _analysis_counter, _requirements_counter, _llm_call_counter
    global _token_counter, _duration_histogram, _latency_histogram
    global _active_analyses_gauge
    
    if _analysis_counter is not None:
        return  # Already initialized
    
    meter = get_meter("rfp-analyzer.metrics")
    
    # Counters
    _analysis_counter = meter.create_counter(
        name="rfp.analysis.count",
        description="Total number of RFP analyses",
        unit="1",
    )
    
    _requirements_counter = meter.create_counter(
        name="rfp.requirements.count",
        description="Total number of requirements extracted",
        unit="1",
    )
    
    _llm_call_counter = meter.create_counter(
        name="rfp.llm.calls",
        description="Total number of LLM API calls",
        unit="1",
    )
    
    _token_counter = meter.create_counter(
        name="rfp.llm.tokens",
        description="Total number of tokens used",
        unit="1",
    )
    
    # Histograms
    _duration_histogram = meter.create_histogram(
        name="rfp.analysis.duration",
        description="Duration of RFP analysis",
        unit="ms",
    )
    
    _latency_histogram = meter.create_histogram(
        name="rfp.llm.latency",
        description="Latency of LLM API calls",
        unit="ms",
    )
    
    # Gauges (using UpDownCounter)
    _active_analyses_gauge = meter.create_up_down_counter(
        name="rfp.analysis.active",
        description="Number of currently active analyses",
        unit="1",
    )


def record_analysis_started(rfp_id: str, source: str = "unknown"):
    """
    Record that an analysis has started.
    
    Args:
        rfp_id: Unique identifier for the RFP
        source: Source of the RFP (e.g., "web", "api", "cli")
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        _analysis_counter.add(
            1,
            attributes={
                "status": "started",
                "source": source,
            }
        )
        
        _active_analyses_gauge.add(1)
        
        logger.debug(f"Recorded analysis started: {rfp_id}")
        
    except Exception as e:
        logger.error(f"Failed to record analysis started: {e}", exc_info=True)


def record_analysis_completed(
    rfp_id: str,
    duration_ms: int,
    requirements_count: int,
    source: str = "unknown"
):
    """
    Record that an analysis has completed successfully.
    
    Args:
        rfp_id: Unique identifier for the RFP
        duration_ms: Duration of the analysis in milliseconds
        requirements_count: Total number of requirements extracted
        source: Source of the RFP
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        _analysis_counter.add(
            1,
            attributes={
                "status": "completed",
                "source": source,
            }
        )
        
        _duration_histogram.record(
            duration_ms,
            attributes={
                "status": "completed",
                "source": source,
            }
        )
        
        _requirements_counter.add(
            requirements_count,
            attributes={
                "source": source,
            }
        )
        
        _active_analyses_gauge.add(-1)
        
        logger.debug(
            f"Recorded analysis completed: {rfp_id}, "
            f"duration={duration_ms}ms, requirements={requirements_count}"
        )
        
    except Exception as e:
        logger.error(f"Failed to record analysis completed: {e}", exc_info=True)


def record_analysis_failed(
    rfp_id: str,
    error: str,
    duration_ms: Optional[int] = None,
    source: str = "unknown"
):
    """
    Record that an analysis has failed.
    
    Args:
        rfp_id: Unique identifier for the RFP
        error: Error message or type
        duration_ms: Duration before failure (if available)
        source: Source of the RFP
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        _analysis_counter.add(
            1,
            attributes={
                "status": "failed",
                "source": source,
                "error_type": error[:50],  # Truncate long errors
            }
        )
        
        if duration_ms is not None:
            _duration_histogram.record(
                duration_ms,
                attributes={
                    "status": "failed",
                    "source": source,
                }
            )
        
        _active_analyses_gauge.add(-1)
        
        logger.debug(f"Recorded analysis failed: {rfp_id}, error={error}")
        
    except Exception as e:
        logger.error(f"Failed to record analysis failed: {e}", exc_info=True)


def record_requirements_extracted(
    agent_name: str,
    count: int,
    category: str = "unknown"
):
    """
    Record requirements extracted by an agent.
    
    Args:
        agent_name: Name of the agent
        count: Number of requirements extracted
        category: Category of requirements (e.g., "functional", "nonfunctional")
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        _requirements_counter.add(
            count,
            attributes={
                "agent": agent_name,
                "category": category,
            }
        )
        
        logger.debug(f"Recorded {count} requirements from {agent_name}")
        
    except Exception as e:
        logger.error(f"Failed to record requirements extracted: {e}", exc_info=True)


def record_llm_call(
    provider: str,
    model: str,
    latency_ms: int,
    status: str = "success",
    error: Optional[str] = None
):
    """
    Record an LLM API call.
    
    Args:
        provider: LLM provider (e.g., "anthropic", "openai")
        model: Model name
        latency_ms: Call latency in milliseconds
        status: Call status ("success", "error", "rate_limited")
        error: Error message if failed
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        attributes = {
            "provider": provider,
            "model": model,
            "status": status,
        }
        
        if error:
            attributes["error_type"] = error[:50]
        
        _llm_call_counter.add(1, attributes=attributes)
        
        _latency_histogram.record(latency_ms, attributes=attributes)
        
        logger.debug(
            f"Recorded LLM call: {provider}/{model}, "
            f"latency={latency_ms}ms, status={status}"
        )
        
    except Exception as e:
        logger.error(f"Failed to record LLM call: {e}", exc_info=True)


def record_token_usage(
    provider: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    total_tokens: Optional[int] = None
):
    """
    Record token usage from an LLM call.
    
    Args:
        provider: LLM provider
        model: Model name
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        total_tokens: Total tokens (calculated if not provided)
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        if total_tokens is None:
            total_tokens = prompt_tokens + completion_tokens
        
        # Record prompt tokens
        _token_counter.add(
            prompt_tokens,
            attributes={
                "provider": provider,
                "model": model,
                "token_type": "prompt",
            }
        )
        
        # Record completion tokens
        _token_counter.add(
            completion_tokens,
            attributes={
                "provider": provider,
                "model": model,
                "token_type": "completion",
            }
        )
        
        # Record total tokens
        _token_counter.add(
            total_tokens,
            attributes={
                "provider": provider,
                "model": model,
                "token_type": "total",
            }
        )
        
        logger.debug(
            f"Recorded token usage: {provider}/{model}, "
            f"prompt={prompt_tokens}, completion={completion_tokens}, total={total_tokens}"
        )
        
    except Exception as e:
        logger.error(f"Failed to record token usage: {e}", exc_info=True)


def record_context_studio_query(
    query_type: str,
    latency_ms: int,
    results_count: int,
    cache_hit: bool = False
):
    """
    Record a Context Studio query.
    
    Args:
        query_type: Type of query (e.g., "vector", "keyword")
        latency_ms: Query latency in milliseconds
        results_count: Number of results returned
        cache_hit: Whether the query hit the cache
    """
    config = get_config()
    if not config.is_enabled or not config.collect_metrics:
        return
    
    try:
        _init_metrics()
        
        # This would use a separate counter for Context Studio queries
        # For now, we'll log it
        logger.debug(
            f"Context Studio query: type={query_type}, "
            f"latency={latency_ms}ms, results={results_count}, cache_hit={cache_hit}"
        )
        
    except Exception as e:
        logger.error(f"Failed to record Context Studio query: {e}", exc_info=True)

# Made with Bob
