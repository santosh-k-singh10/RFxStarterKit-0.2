"""
Test script to generate a collapsible HTML output
"""
from outputs.html_exporter_by_module import export_html_by_module, infer_module
from core.schemas import Requirement, Category, Priority
from pathlib import Path

# Create sample requirements
requirements = [
    Requirement(
        id="REQ-001",
        category=Category.FUNCTIONAL,
        title="User Authentication System",
        description="System must support secure user login with username and password",
        source_section="Security Requirements",
        priority=Priority.MUST,
        confidence=0.95,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=[]
    ),
    Requirement(
        id="REQ-002",
        category=Category.FUNCTIONAL,
        title="Payment Gateway Integration",
        description="Integrate with major payment processors for transaction processing",
        source_section="Payment Features",
        priority=Priority.MUST,
        confidence=0.90,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=[]
    ),
    Requirement(
        id="REQ-003",
        category=Category.NON_FUNCTIONAL,
        title="Dashboard Analytics",
        description="Provide real-time analytics dashboard with charts and metrics",
        source_section="Reporting Module",
        priority=Priority.SHOULD,
        confidence=0.85,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=[]
    ),
]

# Test module inference
print("Testing module inference:")
for req in requirements:
    module = infer_module(req)
    print(f"  {req.id}: {module}")

# Generate HTML
output_path = "outputs/test_collapsible_output.html"
result_path = export_html_by_module(
    requirements=requirements,
    out_path=output_path,
    rfp_title="Test RFP - Collapsible Modules"
)

print(f"\n✅ HTML generated at: {result_path}")
print("\nTo view: Open the file in your browser")