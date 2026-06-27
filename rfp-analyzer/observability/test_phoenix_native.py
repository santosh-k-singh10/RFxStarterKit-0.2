"""
Test Phoenix using native Arize Phoenix SDK

The Phoenix server requires specific format. Let's try using the native SDK.
"""

import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    import phoenix as px
    from phoenix.otel import register
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    
    logger.info("=" * 70)
    logger.info("TESTING PHOENIX NATIVE SDK")
    logger.info("=" * 70)
    
    # Get configuration
    from observability.config import get_config
    config = get_config()
    
    logger.info(f"\nEndpoint: {config.phoenix_endpoint}")
    logger.info(f"API Key: {'*' * 20 if config.phoenix_api_key else 'NOT SET'}")
    logger.info(f"Project: {config.project_name}")
    
    # Try to connect using Phoenix SDK
    logger.info("\n" + "=" * 70)
    logger.info("Attempting Phoenix SDK Connection...")
    logger.info("=" * 70)
    
    # Set Phoenix endpoint
    import os
    os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = config.phoenix_endpoint
    os.environ["PHOENIX_API_KEY"] = config.phoenix_api_key or ""
    
    # Register with Phoenix
    tracer_provider = register(
        project_name=config.project_name,
        endpoint=config.phoenix_endpoint,
    )
    
    logger.info("✅ Phoenix SDK registered successfully")
    
    # Create a test trace
    tracer = trace.get_tracer(__name__)
    
    with tracer.start_as_current_span("test.phoenix_native") as span:
        span.set_attribute("test.type", "native_sdk")
        span.set_attribute("test.project", config.project_name)
        logger.info("✅ Created test span")
    
    logger.info("\n" + "=" * 70)
    logger.info("SUCCESS - Check Phoenix dashboard for traces")
    logger.info("=" * 70)
    
except ImportError as e:
    logger.error("=" * 70)
    logger.error("Phoenix SDK Import Error")
    logger.error("=" * 70)
    logger.error(f"\n{e}")
    logger.error("\nThe arize-phoenix package may not support direct connection.")
    logger.error("Phoenix might be designed for local deployment only.")
    logger.error("\nLet's check the Phoenix documentation for cloud deployment...")
    
except Exception as e:
    logger.error(f"\n❌ Error: {e}", exc_info=True)

# Made with Bob
