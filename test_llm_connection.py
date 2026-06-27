#!/usr/bin/env python3
"""
Simple script to test LLM connection and response
"""
import os
import sys
from pathlib import Path

# Add common directory to path
common_path = Path(__file__).parent / "common"
sys.path.insert(0, str(common_path))

try:
    from openai import OpenAI
    from dotenv import load_dotenv
    
    # Load environment variables
    env_path = Path(__file__).parent / "common" / ".env"
    load_dotenv(env_path)
    
    # Get configuration
    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("OPENAI_API_KEY")
    model_id = os.getenv("MODEL_ID")
    
    print("=" * 60)
    print("LLM CONNECTION TEST")
    print("=" * 60)
    print(f"API Base: {api_base}")
    print(f"Model ID: {model_id}")
    print(f"API Key: {'*' * 20}{api_key[-20:] if api_key else 'NOT SET'}")
    print("=" * 60)
    
    if not all([api_base, api_key, model_id]):
        print("\n[ERROR] Missing required environment variables!")
        print("   Please check your common/.env file")
        sys.exit(1)
    
    # Initialize OpenAI client
    print("\n[*] Initializing OpenAI client...")
    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )
    
    # Test simple completion
    print("\n[*] Testing LLM with a simple prompt...")
    test_prompt = "Hello! Please respond with 'LLM is working correctly' if you can read this message."
    
    response = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "user", "content": test_prompt}
        ],
        max_tokens=100,
        temperature=0.7
    )
    
    # Extract response
    llm_response = response.choices[0].message.content
    
    print("\n[SUCCESS] LLM Response received:")
    print("-" * 60)
    print(llm_response)
    print("-" * 60)
    
    # Additional info
    print(f"\n[INFO] Response Details:")
    print(f"   Model: {response.model}")
    print(f"   Tokens Used: {response.usage.total_tokens if response.usage else 'N/A'}")
    print(f"   Finish Reason: {response.choices[0].finish_reason}")
    
    print("\n[SUCCESS] LLM is working fine and responding correctly!")
    
except ImportError as e:
    print(f"\n[ERROR] Import Error: {e}")
    print("   Please install required packages: pip install openai python-dotenv")
    sys.exit(1)
    
except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}")
    print(f"   {str(e)}")
    print("\n   Possible issues:")
    print("   1. Invalid API key or credentials")
    print("   2. Network connectivity problems")
    print("   3. API endpoint is down or unreachable")
    print("   4. Model ID is incorrect")
    sys.exit(1)

# Made with Bob
