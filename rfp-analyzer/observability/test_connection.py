"""
Test Phoenix Connectivity

Simple script to test connection to Arize Phoenix.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from observability import init_observability, shutdown_observability
from observability.config import get_config
from observability.phoenix_tracer import get_tracer
from opentelemetry import trace

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection():
    """Test connection to Arize Phoenix."""
    
    logger.info("=" * 60)
    logger.info("Testing Arize Phoenix Connection")
    logger.info("=" * 60)
    
    # Load configuration
    config = get_config()
    
    logger.info(f"\nConfiguration:")
    logger.info(f"  Enabled: {config.enabled}")
    logger.info(f"  Phoenix Endpoint: {config.phoenix_endpoint}")
    logger.info(f"  API Key: {'*' * 20 if config.phoenix_api_key else 'NOT SET'}")
    logger.info(f"  Project: {config.project_name}")
    logger.info(f"  Environment: {config.environment}")
    logger.info(f"  Trace Agents: {config.trace_agents}")
    logger.info(f"  Trace LLM Calls: {config.trace_llm_calls}")
    logger.info(f"  Collect Metrics: {config.collect_metrics}")
    
    if not config.is_enabled:
        logger.error("\n❌ Observability is not enabled or API key is missing!")
        logger.info("\nPlease set the following environment variables:")
        logger.info("  OBSERVABILITY_ENABLED=true")
        logger.info("  OBSERVABILITY_PHOENIX_API_KEY=<your-api-key>")
        return False
    
    # Initialize observability
    logger.info("\n" + "=" * 60)
    logger.info("Initializing OpenTelemetry...")
    logger.info("=" * 60)
    
    success = init_observability()
    
    if not success:
        logger.error("\n❌ Failed to initialize observability!")
        return False
    
    logger.info("\n✅ Observability initialized successfully!")
    
    # Create a test trace
    logger.info("\n" + "=" * 60)
    logger.info("Creating test trace...")
    logger.info("=" * 60)
    
    try:
        tracer = get_tracer("test")
        
        with tracer.start_as_current_span("test.connection") as span:
            span.set_attribute("test.type", "connectivity")
            span.set_attribute("test.timestamp", "2026-05-14")
            
            logger.info("\n✅ Test trace created successfully!")
            logger.info(f"   Span ID: {span.get_span_context().span_id}")
            logger.info(f"   Trace ID: {span.get_span_context().trace_id}")
        
        # Shutdown to flush data
        logger.info("\n" + "=" * 60)
        logger.info("Flushing telemetry data...")
        logger.info("=" * 60)
        
        shutdown_observability()
        
        logger.info("\n✅ Telemetry data flushed successfully!")
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ CONNECTION TEST PASSED!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Check the Phoenix dashboard at:")
        logger.info(f"   {config.phoenix_endpoint}")
        logger.info("2. Look for a trace named 'test.connection'")
        logger.info("3. Verify the trace appears in the dashboard")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Error creating test trace: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)

# Made with Bob
