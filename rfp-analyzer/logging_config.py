"""
logging_config.py
-----------------
Centralized logging configuration for the RFP Analyzer.

Provides structured logging with both console and file output.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

import structlog


def setup_logging(
    log_file: str = "./logs/rfp_analyzer.log",
    console_level: str = "INFO",
    file_level: str = "DEBUG"
) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        log_file: Path to the log file
        console_level: Logging level for console output (INFO, DEBUG, WARNING, ERROR)
        file_level: Logging level for file output (INFO, DEBUG, WARNING, ERROR)
    """
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert string levels to logging constants
    console_level_int = getattr(logging, console_level.upper(), logging.INFO)
    file_level_int = getattr(logging, file_level.upper(), logging.DEBUG)
    
    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        level=min(console_level_int, file_level_int),  # Use the lower level
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, mode='a', encoding='utf-8')
        ]
    )
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.dev.ConsoleRenderer(colors=True)
        ],
        wrapper_class=structlog.make_filtering_bound_logger(console_level_int),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )
    
    # Set levels for specific loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

# Made with Bob
