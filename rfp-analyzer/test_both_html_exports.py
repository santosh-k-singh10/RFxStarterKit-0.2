"""
Test script for both HTML export functionalities
"""

from core.schemas import Requirement, Category, Priority
from outputs.html_exporter import export_html
from outputs.html_exporter_by_module import export_html_by_module

# Create sample requirements with diverse content
requirements = [
    # User Management
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
        id="FR-002",
        category=Category.FUNCTIONAL,
        title="User Profile Management",
        description="Users must be able to create, update, and manage their profile information including contact details and preferences.",
        source_section="User Management",
        page_ref="15",
        priority=Priority.MUST,
        confidence=0.92,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=[]
    ),
    # Payment Processing
    Requirement(
        id="FR-003",
        category=Category.FUNCTIONAL,
        title="Payment Gateway Integration",
        description="The system must integrate with major payment gateways to process credit card and digital wallet transactions.",
        source_section="Payment Processing",
        page_ref="22",
        priority=Priority.MUST,
        confidence=0.89,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=["NFR-005"]
    ),
    # Performance
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
        id="NFR-005",
        category=Category.NON_FUNCTIONAL,
        title="Transaction Processing Speed",
        description="Payment transactions must be processed within 5 seconds to ensure good user experience.",
        source_section="Performance Requirements",
        page_ref="19",
        priority=Priority.SHOULD,
        confidence=0.85,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=["FR-003"]
    ),
    # Compliance
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
    # Reporting
    Requirement(
        id="FR-004",
        category=Category.FUNCTIONAL,
        title="Analytics Dashboard",
        description="The system must provide a comprehensive analytics dashboard with real-time reporting capabilities.",
        source_section="Reporting Requirements",
        page_ref="30",
        priority=Priority.SHOULD,
        confidence=0.87,
        ambiguity_flag=False,
        clarification_question="",
        related_ids=[]
    ),
    # Ambiguity
    Requirement(
        id="AMB-001",
        category=Category.AMBIGUITY,
        title="Data Retention Period",
        description="The document mentions 'appropriate data retention' without specific timeframes.",
        source_section="Data Management",
        page_ref="35",
        priority=Priority.SHOULD,
        confidence=0.75,
        ambiguity_flag=True,
        clarification_question="What is the specific data retention period required?",
        related_ids=[]
    ),
]

# Export both versions
print("=" * 70)
print("Generating HTML Reports...")
print("=" * 70)

# Version 1: Grouped by Category
category_path = export_html(requirements, "outputs/test_html_by_category.html", rfp_title="Sample RFP Analysis")
print(f"\n✅ HTML Report (by Category) generated!")
print(f"📄 File: {category_path}")
print(f"🌐 Open: file:///{category_path}")

# Version 2: Grouped by Module
module_path = export_html_by_module(requirements, "outputs/test_html_by_module.html", rfp_title="Sample RFP Analysis