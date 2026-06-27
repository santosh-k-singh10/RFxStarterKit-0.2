"""
Test script to verify the generate-architecture flow end-to-end with logging.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_preferences_endpoint():
    """Test POST /api/preferences"""
    print("\n" + "=" * 70)
    print("TEST 1: POST /api/preferences")
    print("=" * 70)
    
    preferences_data = {
        "approach": "greenfield",
        "deployment": "cloud",
        "cloud": "aws",
        "platform": [],
        "compliance": ["gdpr"],
        "channels": ["web", "mobile_native"],
        "integration": "rest",
        "timeline": "phased",
        "tech_estate": "PostgreSQL, Redis, React",
        "skill_notes": "Team experienced with Node.js and Python"
    }
    
    print(f"\nSending preferences: {json.dumps(preferences_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/preferences",
        json=preferences_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        print("[OK] Preferences validated successfully")
        result = response.json()
        print(f"\nInferred domain context: {result.get('inferred_domain_context')}")
        return result
    else:
        print(f"[FAIL] Failed: {response.text}")
        return None


def test_analyze_endpoint(preferences):
    """Test POST /api/analyze"""
    print("\n" + "=" * 70)
    print("TEST 2: POST /api/analyze")
    print("=" * 70)
    
    requirements = """
# Requirements

## Functional Requirements

### FR-001: User Authentication
Users must be able to register and login using email and password.

### FR-002: Product Catalog
System must display a searchable product catalog with filtering capabilities.

### FR-003: Shopping Cart
Users can add items to cart and proceed to checkout.

## Non-Functional Requirements

### NFR-001: Performance
System must handle 1000 concurrent users with response time < 2 seconds.

### NFR-002: Security
All data must be encrypted in transit and at rest.
"""
    
    analyze_data = {
        "preferences": preferences,
        "requirements": requirements,
        "project_name": "E-Commerce Platform"
    }
    
    print(f"\nSending analysis request for project: {analyze_data['project_name']}")
    print(f"Requirements length: {len(requirements)} characters")
    
    response = requests.post(
        f"{BASE_URL}/api/analyze",
        json=analyze_data,
        headers={"Content-Type": "application/json"},
        timeout=120  # 2 minutes timeout for LLM call
    )
    
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        print("[OK] Architecture generated successfully")
        result = response.json()
        print(f"\nArchitecture Summary:")
        print(f"  - Components: {result.get('summary', {}).get('component_count', 0)}")
        print(f"  - Domains: {result.get('summary', {}).get('domain_count', 0)}")
        print(f"  - Risks: {len(result.get('risks', []))}")
        print(f"  - Story Points (mid): {result.get('summary', {}).get('total_story_points_mid', 0)}")
        return result
    else:
        print(f"[FAIL] Failed: {response.text}")
        return None


def test_health_endpoint():
    """Test GET /api/health"""
    print("\n" + "=" * 70)
    print("TEST 0: GET /api/health")
    print("=" * 70)
    
    response = requests.get(f"{BASE_URL}/api/health")
    print(f"\nResponse Status: {response.status_code}")
    if response.status_code == 200:
        print("[OK] Health check passed")
        print(f"Response: {response.json()}")
        return True
    else:
        print(f"[FAIL] Health check failed: {response.text}")
        return False


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("ARCHITECTURE FLOW END-TO-END TEST")
    print("=" * 70)
    print("\nThis test will verify the complete generate-architecture flow")
    print("and display all logging output in the terminal.")
    print("\nMake sure the server is running: python run.py")
    print("=" * 70)
    
    try:
        # Test 0: Health check
        if not test_health_endpoint():
            print("\n[FAIL] Server not responding. Make sure it's running.")
            exit(1)
        
        # Test 1: Preferences
        preferences = test_preferences_endpoint()
        if not preferences:
            print("\n[FAIL] Preferences test failed")
            exit(1)
        
        # Test 2: Architecture analysis
        architecture = test_analyze_endpoint(preferences)
        if not architecture:
            print("\n[FAIL] Architecture analysis test failed")
            exit(1)
        
        print("\n" + "=" * 70)
        print("[SUCCESS] ALL TESTS PASSED")
        print("=" * 70)
        print("\nCheck the server terminal for detailed logging output.")
        print("You should see logs for each step of the flow:")
        print("  1. Preferences collection and validation")
        print("  2. Architecture input creation")
        print("  3. LLM API calls with token usage")
        print("  4. Response parsing")
        print("  5. Component and domain extraction")
        print("=" * 70)
        
    except requests.exceptions.ConnectionError:
        print("\n[FAIL] Could not connect to server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"\n[FAIL] Test failed with error: {e}")
        import traceback
        traceback.print_exc()

# Made with Bob
