"""
run.py — Start the RFP Analyzer API server.

Loads configuration from .env and starts uvicorn.
"""

import os
import sys
import logging
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
    stream=sys.stdout,
    force=True,
)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    
    print("=" * 70)
    print("Starting RFP Analyzer API v1.2")
    print("=" * 70)
    print(f"Server: http://localhost:{port}")
    print(f"API Docs: http://localhost:{port}/docs")
    print(f"Preferences Form: http://localhost:{port}/")
    print("=" * 70)
    print()
    
    # Check LLM configuration
    try:
        from config import config
        if config.is_llm_configured():
            print(f"[OK] LLM configured: {config.get_llm_type()}")
            if config.OPENAI_API_BASE:
                print(f"     Base URL: {config.OPENAI_API_BASE}")
                print(f"     Model: {config.MODEL_ID}")
        else:
            print("[WARN] LLM not configured. Set credentials in .env file.")
    except Exception as e:
        print(f"[WARN] Could not load config: {e}")
    
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 70)
    print()
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
        access_log=True,
        log_config={
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "uvicorn.logging.DefaultFormatter",
                    "fmt": "%(asctime)s  %(levelprefix)s %(name)s  %(message)s",
                    "use_colors": None,
                },
                "access": {
                    "()": "uvicorn.logging.AccessFormatter",
                    "fmt": "%(asctime)s  %(levelprefix)s %(name)s  %(client_addr)s - \"%(request_line)s\" %(status_code)s",
                    "use_colors": None,
                },
            },
            "handlers": {
                "default": {
                    "formatter": "default",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
                "access": {
                    "formatter": "access",
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                },
            },
            "loggers": {
                "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": "INFO", "propagate": False},
                "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
            },
            "root": {"handlers": ["default"], "level": "INFO"},
        },
    )
