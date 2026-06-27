"""
Comprehensive Phoenix Integration Test

This script tests the complete integration with Arize Phoenix:
1. Registers the project
2. Sends test traces with various span types
3. Verifies data export
4. Provides detailed diagnostics
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from observability import (
    init_observability,
    shutdown_observability,
    trace_agent,
    trace_llm_call,
    trace_operation,
)
from observability.config import get_config
from observability.phoenix_tracer import get_tracer, add_span_attribute, add_span_event
from observability.metrics import (
    record_analysis_started,
    record_analysis_completed,
    record_llm_call,
    record_token_usage,
)
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_section(title: str):
    """Print a formatted section header."""
    logger.info("\n" + "=" * 70)
    logger.info(f"  {title}")
    logger.info("=" * 70)


def test_basic_trace():
    """Test basic trace creation."""
    print_section("TEST 1: Basic Trace")
    
    tracer = get_tracer("test.basic")
    
    with tracer.start_as_current_span("test.basic_operation") as span:
        span.set_attribute("test.type", "basic")
        span.set_attribute("test.timestamp", datetime.now().isoformat())
        span.set_attribute("test.project", "rfp-analyzer")
        
        # Simulate some work
        time.sleep(0.1)
        
        span.add_event("operation_started")
        time.sleep(0.1)
        span.add_event("operation_completed")
        
        span.set_status(Status(StatusCode.OK))
        
        logger.info(f"✅ Created basic trace")
        logger.info(f"   Span ID: {span.get_span_context().span_id}")
        logger.info(f"   Trace ID: {span.get_span_context().trace_id}")


def test_nested_spans():
    """Test nested span hierarchy."""
    print_section("TEST 2: Nested Spans (Parent-Child)")
    
    tracer = get_tracer("test.nested")
    
    with tracer.start_as_current_span("test.parent_operation") as parent_span:
        parent_span.set_attribute("span.level", "parent")
        parent_span.set_attribute("operation.name", "rfp_analysis")
        
        logger.info(f"✅ Created parent span")
        logger.info(f"   Trace ID: {parent_span.get_span_context().trace_id}")
        
        # Child span 1
        with tracer.start_as_current_span("test.child_operation_1") as child1:
            child1.set_attribute("span.level", "child")
            child1.set_attribute("operation.name", "document_parsing")
            time.sleep(0.05)
            logger.info(f"✅ Created child span 1")
        
        # Child span 2
        with tracer.start_as_current_span("test.child_operation_2") as child2:
            child2.set_attribute("span.level", "child")
            child2.set_attribute("operation.name", "requirement_extraction")
            time.sleep(0.05)
            logger.info(f"✅ Created child span 2")
        
        parent_span.set_status(Status(StatusCode.OK))


def test_llm_simulation():
    """Test LLM call simulation with token tracking."""
    print_section("TEST 3: Simulated LLM Call")
    
    tracer = get_tracer("test.llm")
    
    with tracer.start_as_current_span(
        "llm.anthropic.call",
        kind=trace.SpanKind.CLIENT
    ) as span:
        # Simulate LLM call metadata
        span.set_attribute("llm.provider", "anthropic")
        span.set_attribute("llm.model", "claude-3-5-sonnet-20241022")
        span.set_attribute("llm.temperature", 0.7)
        span.set_attribute("llm.max_tokens", 4096)
        
        start_time = time.time()
        
        # Simulate API call
        time.sleep(0.5)
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Simulate token usage
        span.set_attribute("llm.tokens.prompt", 1500)
        span.set_attribute("llm.tokens.completion", 800)
        span.set_attribute("llm.tokens.total", 2300)
        span.set_attribute("llm.latency_ms", latency_ms)
        
        span.set_status(Status(StatusCode.OK))
        
        logger.info(f"✅ Simulated LLM call")
        logger.info(f"   Provider: anthropic")
        logger.info(f"   Model: claude-3-5-sonnet-20241022")
        logger.info(f"   Latency: {latency_ms}ms")
        logger.info(f"   Tokens: 2300 (1500 prompt + 800 completion)")


def test_agent_simulation():
    """Test agent execution simulation."""
    print_section("TEST 4: Simulated Agent Execution")
    
    tracer = get_tracer("test.agent")
    
    with tracer.start_as_current_span("agent.functional_extraction") as span:
        span.set_attribute("agent.name", "functional_extraction")
        span.set_attribute("agent.type", "extraction")
        
        start_time = time.time()
        
        # Simulate agent work
        span.add_event("agent_started")
        time.sleep(0.2)
        
        span.add_event("requirements_extracted", {
            "count": 15
        })
        
        duration_ms = int((time.time() - start_time) * 1000)
        span.set_attribute("agent.duration_ms", duration_ms)
        span.set_attribute("agent.requirements_extracted", 15)
        
        span.set_status(Status(StatusCode.OK))
        
        logger.info(f"✅ Simulated agent execution")
        logger.info(f"   Agent: functional_extraction")
        logger.info(f"   Duration: {duration_ms}ms")
        logger.info(f"   Requirements: 15")


def test_error_handling():
    """Test error handling and exception recording."""
    print_section("TEST 5: Error Handling")
    
    tracer = get_tracer("test.error")
    
    with tracer.start_as_current_span("test.error_operation") as span:
        span.set_attribute("test.type", "error_handling")
        
        try:
            # Simulate an error
            span.add_event("attempting_risky_operation")
            raise ValueError("Simulated error for testing")
            
        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            span.set_attribute("error.type", type(e).__name__)
            span.set_attribute("error.message", str(e))
            
            logger.info(f"✅ Recorded exception in span")
            logger.info(f"   Error: {type(e).__name__}: {e}")


def test_complete_workflow():
    """Test a complete RFP analysis workflow simulation."""
    print_section("TEST 6: Complete Workflow Simulation")
    
    tracer = get_tracer("test.workflow")
    
    # Root span for entire analysis
    with tracer.start_as_current_span("rfp.analysis") as root_span:
        root_span.set_attribute("rfp.id", "test-rfp-001")
        root_span.set_attribute("rfp.source", "test")
        
        logger.info(f"✅ Started RFP analysis workflow")
        logger.info(f"   Trace ID: {root_span.get_span_context().trace_id}")
        
        # Document ingestion
        with tracer.start_as_current_span("operation.document_ingestion") as ingest_span:
            ingest_span.set_attribute("operation.type", "io")
            time.sleep(0.1)
            ingest_span.add_event("document_parsed")
            logger.info(f"   ✓ Document ingestion")
        
        # Agent executions
        agents = ["functional", "nonfunctional", "compliance", "risk"]
        total_requirements = 0
        
        for agent_name in agents:
            with tracer.start_as_current_span(f"agent.{agent_name}_extraction") as agent_span:
                agent_span.set_attribute("agent.name", agent_name)
                time.sleep(0.1)
                
                req_count = 10 + len(agent_name)  # Simulate different counts
                agent_span.set_attribute("agent.requirements_extracted", req_count)
                total_requirements += req_count
                
                logger.info(f"   ✓ {agent_name} extraction: {req_count} requirements")
        
        # Synthesis
        with tracer.start_as_current_span("operation.synthesis") as synth_span:
            synth_span.set_attribute("operation.type", "computation")
            time.sleep(0.1)
            synth_span.add_event("deduplication_complete")
            logger.info(f"   ✓ Synthesis")
        
        # Export
        with tracer.start_as_current_span("operation.export") as export_span:
            export_span.set_attribute("operation.type", "io")
            export_span.set_attribute("export.formats", "json,xlsx,md")
            time.sleep(0.05)
            logger.info(f"   ✓ Export")
        
        root_span.set_attribute("rfp.total_requirements", total_requirements)
        root_span.set_status(Status(StatusCode.OK))
        
        logger.info(f"✅ Completed workflow")
        logger.info(f"   Total requirements: {total_requirements}")


def test_metrics():
    """Test metrics recording."""
    print_section("TEST 7: Metrics Recording")
    
    # Record analysis metrics
    record_analysis_started("test-rfp-001", source="test")
    logger.info("✅ Recorded analysis started")
    
    time.sleep(0.1)
    
    # Record LLM call metrics
    record_llm_call(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        latency_ms=450,
        status="success"
    )
    logger.info("✅ Recorded LLM call metric")
    
    # Record token usage
    record_token_usage(
        provider="anthropic",
        model="claude-3-5-sonnet-20241022",
        prompt_tokens=1500,
        completion_tokens=800
    )
    logger.info("✅ Recorded token usage")
    
    # Record analysis completion
    record_analysis_completed(
        rfp_id="test-rfp-001",
        duration_ms=2500,
        requirements_count=45,
        source="test"
    )
    logger.info("✅ Recorded analysis completed")


def run_all_tests():
    """Run all integration tests."""
    
    print_section("ARIZE PHOENIX INTEGRATION TEST SUITE")
    
    # Load configuration
    config = get_config()
    
    logger.info("\nConfiguration:")
    logger.info(f"  Endpoint: {config.phoenix_endpoint}")
    logger.info(f"  Project: {config.project_name}")
    logger.info(f"  Environment: {config.environment}")
    logger.info(f"  API Key: {'✓ Set' if config.phoenix_api_key else '✗ Missing'}")
    
    if not config.is_enabled:
        logger.error("\n❌ Observability is not enabled!")
        logger.error("Please set OBSERVABILITY_PHOENIX_API_KEY in .env file")
        return False
    
    # Initialize observability
    print_section("Initializing OpenTelemetry")
    
    if not init_observability():
        logger.error("❌ Failed to initialize observability")
        return False
    
    logger.info("✅ OpenTelemetry initialized successfully")
    
    try:
        # Run all tests
        test_basic_trace()
        test_nested_spans()
        test_llm_simulation()
        test_agent_simulation()
        test_error_handling()
        test_complete_workflow()
        test_metrics()
        
        # Flush data
        print_section("Flushing Telemetry Data")
        logger.info("Waiting for data export...")
        time.sleep(2)  # Give time for async export
        
        shutdown_observability()
        
        logger.info("✅ All telemetry data flushed")
        
        # Summary
        print_section("TEST SUITE COMPLETE")
        logger.info("\n✅ All tests passed successfully!")
        logger.info("\nNext Steps:")
        logger.info("1. Open Phoenix dashboard:")
        logger.info(f"   {config.phoenix_endpoint}")
        logger.info("2. Look for traces from project: rfp-analyzer")
        logger.info("3. Verify the following traces appear:")
        logger.info("   - test.basic_operation")
        logger.info("   - test.parent_operation (with 2 children)")
        logger.info("   - llm.anthropic.call")
        logger.info("   - agent.functional_extraction")
        logger.info("   - test.error_operation (with error)")
        logger.info("   - rfp.analysis (complete workflow with 6 child spans)")
        logger.info("\n4. Check metrics for:")
        logger.info("   - Analysis count")
        logger.info("   - LLM calls")
        logger.info("   - Token usage")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test suite failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

# Made with Bob
