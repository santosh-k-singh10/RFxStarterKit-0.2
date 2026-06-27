"""
Phoenix Connection Diagnostics

Diagnose connection issues with Arize Phoenix server.
"""

import sys
import requests
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from observability.config import get_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_phoenix_endpoints():
    """Test various Phoenix endpoints to find the correct one."""
    
    config = get_config()
    base_url = config.phoenix_endpoint
    api_key = config.phoenix_api_key
    
    logger.info("=" * 70)
    logger.info("PHOENIX CONNECTION DIAGNOSTICS")
    logger.info("=" * 70)
    logger.info(f"\nBase URL: {base_url}")
    logger.info(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test endpoints
    endpoints = [
        ("Root", base_url),
        ("Health", f"{base_url}/health"),
        ("Version", f"{base_url}/version"),
        ("Projects", f"{base_url}/projects"),
        ("OTLP Traces", f"{base_url}/v1/traces"),
        ("API Traces", f"{base_url}/api/traces"),
        ("Ingest", f"{base_url}/ingest"),
    ]
    
    logger.info("\n" + "=" * 70)
    logger.info("TESTING ENDPOINTS")
    logger.info("=" * 70)
    
    for name, url in endpoints:
        try:
            logger.info(f"\nTesting: {name}")
            logger.info(f"URL: {url}")
            
            response = requests.get(url, headers=headers, timeout=10)
            
            logger.info(f"Status: {response.status_code}")
            logger.info(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                logger.info(f"✅ SUCCESS")
                try:
                    logger.info(f"Response: {response.json()}")
                except:
                    logger.info(f"Response: {response.text[:200]}")
            else:
                logger.info(f"❌ FAILED: {response.status_code} - {response.reason}")
                logger.info(f"Response: {response.text[:200]}")
                
        except Exception as e:
            logger.error(f"❌ ERROR: {e}")
    
    # Test OTLP endpoint with POST
    logger.info("\n" + "=" * 70)
    logger.info("TESTING OTLP TRACE EXPORT (POST)")
    logger.info("=" * 70)
    
    otlp_url = f"{base_url}/v1/traces"
    logger.info(f"URL: {otlp_url}")
    
    # Minimal OTLP payload
    test_payload = {
        "resourceSpans": [{
            "resource": {
                "attributes": [{
                    "key": "service.name",
                    "value": {"stringValue": "rfp-analyzer"}
                }]
            },
            "scopeSpans": [{
                "scope": {"name": "test"},
                "spans": [{
                    "traceId": "00000000000000000000000000000001",
                    "spanId": "0000000000000001",
                    "name": "test.span",
                    "kind": 1,
                    "startTimeUnixNano": "1000000000",
                    "endTimeUnixNano": "2000000000",
                    "attributes": []
                }]
            }]
        }]
    }
    
    try:
        response = requests.post(
            otlp_url,
            json=test_payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        logger.info(f"Status: {response.status_code}")
        logger.info(f"Response: {response.text}")
        
        if response.status_code in [200, 202]:
            logger.info("✅ OTLP endpoint accepts traces")
        else:
            logger.error(f"❌ OTLP endpoint rejected: {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
    
    # Check if we need to use Protobuf instead of JSON
    logger.info("\n" + "=" * 70)
    logger.info("RECOMMENDATION")
    logger.info("=" * 70)
    logger.info("\nThe Phoenix server may require:")
    logger.info("1. Protobuf format instead of JSON")
    logger.info("2. Different endpoint URL")
    logger.info("3. Different authentication method")
    logger.info("\nCheck Phoenix documentation for:")
    logger.info("- Correct OTLP endpoint URL")
    logger.info("- Required content-type (application/x-protobuf vs application/json)")
    logger.info("- Authentication header format")


if __name__ == "__main__":
    test_phoenix_endpoints()

# Made with Bob
