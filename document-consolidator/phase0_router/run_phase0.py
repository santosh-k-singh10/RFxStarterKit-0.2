"""
run_phase0.py
-------------
Startup script for Phase 0 Document Router standalone server.

Usage:
    python run_phase0.py
    python run_phase0.py --port 8001
    python run_phase0.py --host 0.0.0.0 --port 8001 --reload
"""

import argparse
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Phase 0 Document Router - Standalone Server"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8001,
        help="Port to bind to (default: 8001)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("📄 Phase 0 Document Router - Standalone Server")
    print("="*60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"URL: http://{args.host}:{args.port}")
    print(f"API Docs: http://{args.host}:{args.port}/docs")
    print("="*60)
    print("\nFeatures:")
    print("  ✓ Multi-document classification")
    print("  ✓ Intelligent chunking")
    print("  ✓ Conflict detection")
    print("  ✓ Phase-aware routing")
    print("="*60 + "\n")
    
    # Import and run
    import uvicorn
    uvicorn.run(
        "phase0.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

if __name__ == "__main__":
    main()

# Made with Bob
