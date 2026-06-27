"""Test the collapsible module HTML exporter"""

from pathlib import Path
from core.schemas import Requirement, Category, Priority
from outputs.html_exporter_by_module import export_html_by_module

# Create sample requirements
requirements = [
    Requirement(
        id="FR-001",
        title="User Login System",
        description="Users should be able to log in with email and password",
        category=Category.FUNCTIONAL,
        priority=Priority.MUST,
        source_section="Authentication",
        confidence=0.95,
        ambiguity_flag=False
    ),
    Requirement(
        id="FR-002",
        title="Password Reset",
        description="Users should be able to reset forgotten passwords via email",
        category=Category.FUNCTIONAL,
        priority=Priority.MUST,
        source_section="Authentication",
        confidence=0.90,
        ambiguity_flag=False
    ),
    Requirement(
        id="NFR-001",
        title="Page Load Time",
        description="Pages should load within 2 seconds",
        category=Category.NON_FUNCTIONAL,
        priority=Priority.SHOULD,
        source_section="Performance",
        confidence=0.85,
        ambiguity_flag=False
    ),
]

# Export to HTML
output_path = "outputs/test_collapsible_modules.html"
export_html_by_module(requirements, output_path, "Test Collapsible Modules")

print(f"✅ Generated collapsible HTML: {output_path}")
print("Open this file in your browser to see the collapsible modules!")