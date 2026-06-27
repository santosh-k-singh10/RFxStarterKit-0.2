"""
Test script for HTML export functionality
"""

from core.schemas import Requirement, Category, Priority
from outputs.html_exporter import export_html

# Create sample requirements
requirements = [
    Requirement(
        id="FR-001",
        category=Category.FUNCTIONAL,
        title="User Authentication System",
        description="The system must provide secure user authentication with multi-factor authentication support.",
        source_section="Security Requirements",
        page_ref="12",
        priority=Priority.MUST,
        confidence=0.95,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=["NFR-003", "CR-001"]
    ),
    Requirement(
        id="NFR-003",
        category=Category.NON_FUNCTIONAL,
        title="Response Time",
        description="The system must respond to user requests within 2 seconds under normal load.",
        source_section="Performance Requirements",
        page_ref="18",
        priority=Priority.MUST,
        confidence=0.88,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=["FR-001"]
    ),
    Requirement(
        id="CR-001",
        category=Category.COMPLIANCE,
        title="GDPR Compliance",
        description="The system must comply with GDPR regulations for data protection and privacy.",
        source_section="Compliance",
        page_ref="25",
        priority=Priority.MUST,
        confidence=0.92,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=["FR-001"]
    ),
    Requirement(
        id="AMB-001",
        category=Category.AMBIGUITY,
        title="Data Retention Period",
        description="The document mentions 'appropriate data retention' without specific timeframes.",
        source_section="Data Management",
        page_ref="30",
        priority=Priority.SHOULD,
        confidence=0.75,
        ambiguity_flag=True,
        clarification_question="What is the specific data retention period required?",
        related_ids=[]
    ),
]

# Export to HTML
output_path = "outputs/test_html_report.html"
result_path = export_html(requirements, output_path, rfp_title="Sample RFP Analysis")

print(f"✅ HTML report generated successfully!")
print(f"📄 File location: {result_path}")
print(f"\n🌐 Open in browser: file:///{result_path}")
print(f"\nTotal requirements exported: {len(requirements)}")