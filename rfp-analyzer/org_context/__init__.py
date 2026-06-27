"""
org_context package
-------------------
Organizational context management for RFP Analyzer.

This package provides:
- Context loading and validation
- Organizational standards and templates
- Domain knowledge management
- Integration with MCP servers
"""

from .context_manager import (
    ContextManager,
    get_context_manager,
    initialize_context_manager,
)
from .context_schema import (
    OrganizationContext,
    TechStack,
    ComplianceRequirements,
    NamingConventions,
    PriorityMapping,
    RiskThresholds,
    OutputPreferences,
)

__all__ = [
    "ContextManager",
    "get_context_manager",
    "initialize_context_manager",
    "OrganizationContext",
    "TechStack",
    "ComplianceRequirements",
    "NamingConventions",
    "PriorityMapping",
    "RiskThresholds",
    "OutputPreferences",
]

__version__ = "1.0.0"

# Made with Bob
