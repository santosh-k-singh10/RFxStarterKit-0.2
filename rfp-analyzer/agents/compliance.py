"""
agents/compliance.py
--------------------
Extracts COMPLIANCE and REGULATORY requirements from RFP chunks.

Examples: GDPR, HIPAA, SOC 2, ISO 27001, PCI-DSS, WCAG 2.1 AA,
          government data residency rules, sector-specific mandates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import structlog
from agents.base import call_claude
from core.schemas import Category, DocumentChunk, Requirement

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext

log = structlog.get_logger()

SYSTEM_PROMPT = """You are a compliance and legal analyst extracting COMPLIANCE, REGULATORY, and CERTIFICATION requirements from RFP documents.

Look specifically for:
- Data privacy laws: GDPR, CCPA, PDPA, DPDP Act (India)
- Security standards: ISO 27001, SOC 2 Type II, NIST, CIS benchmarks
- Healthcare: HIPAA, HL7, FHIR
- Payment: PCI-DSS
- Government / public sector: FedRAMP, IL ratings, government cloud requirements
- Accessibility: WCAG 2.0/2.1 AA/AAA, Section 508, EN 301 549
- Industry-specific: SEBI, RBI, IRDA, RERA (India context), FSA, MiFID
- Data residency: "data must reside in India / EU / US"
- Audit and logging obligations
- Certification requirements for the vendor

Output a JSON array with EXACTLY these fields:
[
  {
    "title": "Standard or regulation name + what it requires",
    "description": "What specifically must be done to comply. Include standard version/level if mentioned.",
    "source_section": "Section heading",
    "priority": "must | should | could | wont",
    "confidence": 0.95,
    "ambiguity_flag": false,
    "clarification_question": null,
    "raw_excerpt": "Exact source text"
  }
]

RULES:
- If a regulation is named but the specific obligation is unclear, set ambiguity_flag=true
- Vendor certifications ("the vendor must hold ISO 27001") are compliance requirements
- Return [] if no compliance content is found in the chunk
- Output ONLY valid JSON."""


def extract_compliance(
    chunks: list[DocumentChunk],
    id_start: int = 1,
    org_context: Optional[OrganizationContext] = None,
) -> list[Requirement]:
    """
    Extract compliance requirements from all document chunks.
    
    Parameters
    ----------
    chunks : list[DocumentChunk]
        Document chunks to process
    id_start : int
        Starting ID counter
    org_context : Optional[OrganizationContext]
        Organizational context for context-aware extraction
    """
    # Get context if not provided
    if org_context is None:
        try:
            from org_context import get_context_manager
            context_mgr = get_context_manager()
            org_context = context_mgr.get_context() if context_mgr else None
        except ImportError:
            org_context = None
    requirements: list[Requirement] = []
    counter = id_start

    for chunk in chunks:
        if not chunk.is_substantial():
            continue

        user_content = (
            f"Section: {chunk.section}\n"
            f"Page: {chunk.page}\n\n"
            f"{chunk.text}"
        )

        items = call_claude(SYSTEM_PROMPT, user_content, org_context=org_context)

        for item in items:
            try:
                req_id = _generate_requirement_id(counter, org_context)
                req = Requirement(
                    id=req_id,
                    category=Category.COMPLIANCE,
                    page_ref=str(chunk.page),
                    **_sanitise(item),
                )
                requirements.append(req)
                counter += 1
            except Exception as exc:  # noqa: BLE001
                log.warning("compliance_parse_error", error=str(exc))

    log.info("compliance_extraction_done", count=len(requirements))
    return requirements


def _generate_requirement_id(counter: int, org_context: Optional[OrganizationContext]) -> str:
    """Generate requirement ID using organizational context naming conventions."""
    if not org_context:
        return f"CR-{counter:03d}"
    
    prefix = org_context.naming_conventions.compliance_prefix
    separator = org_context.naming_conventions.separator
    padding = org_context.naming_conventions.padding
    
    return f"{prefix}{separator}{counter:0{padding}d}"


def _sanitise(item: dict) -> dict:
    allowed = {
        "title", "description", "source_section",
        "priority", "confidence", "ambiguity_flag",
        "clarification_question", "raw_excerpt",
    }
    clean = {k: v for k, v in item.items() if k in allowed}
    raw_priority = str(clean.get("priority", "must")).lower().strip()
    priority_map = {"must": "must", "should": "should", "could": "could", "wont": "wont", "won't": "wont"}
    clean["priority"] = priority_map.get(raw_priority, "must")
    conf = clean.get("confidence", 0.9)
    try:
        clean["confidence"] = max(0.0, min(1.0, float(conf)))
    except (TypeError, ValueError):
        clean["confidence"] = 0.9
    return clean
