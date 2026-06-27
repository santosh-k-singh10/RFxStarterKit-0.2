"""
Test Phoenix using arize-phoenix-otel SDK

Based on Phoenix documentation for cloud deployment.
"""

import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from observability.config import get_config
from phoenix.otel import register
from opentelemetry import trace

def test_phoenix_otel():
    """Test Phoenix using the official OTEL SDK."""
    
    logger.info("=" * 70)
    logger.info("PHOENIX OTEL SDK TEST")
    logger.info("=" * 70)
    
    config = get_config()
    
    logger.info(f"\nConfiguration:")
    logger.info(f"  Endpoint: {config.phoenix_endpoint}")
    logger.info(f"  API Key: {'*' * 20 if config.phoenix_api_key else 'NOT SET'}")
    logger.info(f"  Project: {config.project_name}")
    
    if not config.phoenix_api_key:
        logger.error("\n❌ API Key not set!")
        return False
    
    try:
        logger.info("\n" + "=" * 70)
        logger.info("Registering with Phoenix...")
        logger.info("=" * 70)
        
        # Register using Phoenix OTEL SDK
        tracer_provider = register(
            project_name=config.project_name,
            endpoint=config.phoenix_endpoint,
            auto_instrument=True
        )
        
        logger.info("✅ Phoenix OTEL registered successfully")
        
        # Create test traces
        logger.info("\n" + "=" * 70)
        logger.info("Creating Test Traces...")
        logger.info("=" * 70)
        
        tracer = trace.get_tracer(__name__)
        
        # Test 1: Simple trace
        with tracer.start_as_current_span("test.simple") as span:
            span.set_attribute("test.type", "simple")
            span.set_attribute("project", config.project_name)
            time.sleep(0.1)
            logger.info("✅ Created simple trace")
        
        # Test 2: Nested trace
        with tracer.start_as_current_span("test.workflow") as root:
            root.set_attribute("workflow.type", "rfp_analysis")
            
            with tracer.start_as_current_span("test.step1") as step1:
                step1.set_attribute("step", "parsing")
                time.sleep(0.05)
            
            with tracer.start_as_current_span("test.step2") as step2:
                step2.set_attribute("step", "extraction")
                time.sleep(0.05)
            
            logger.info("✅ Created nested workflow trace")
        
        # Test 3: LLM simulation
        with tracer.start_as_current_span("llm.call") as llm_span:
            llm_span.set_attribute("llm.provider", "anthropic")
            llm_span.set_attribute("llm.model", "claude-3-5-sonnet")
            llm_span.set_attribute("llm.tokens.prompt", 1500)
            llm_span.set_attribute("llm.tokens.completion", 800)
            time.sleep(0.2)
            logger.info("✅ Created LLM call trace")
        
        logger.info("\n" + "=" * 70)
        logger.info("Flushing traces...")
        logger.info("=" * 70)
        
        # Give time for traces to be sent
        time.sleep(2)
        
        logger.info("\n" + "=" * 70)
        logger.info("✅ TEST COMPLETE")
        logger.info("=" * 70)
        logger.info("\nNext Steps:")
        logger.info("1. Open Phoenix dashboard:")
        logger.info(f"   https://agentstudio.servicesessentials.ibm.com/observability")
        logger.info("2. Look for project: rfp-analyzer")
        logger.info("3. Verify traces appear:")
        logger.info("   - test.simple")
        logger.info("   - test.workflow (with 2 child spans)")
        logger.info("   - llm.call")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_phoenix_otel()
    sys.exit(0 if success else 1)

# Made with Bob
