"""
agents/risk.py
--------------
Identifies DELIVERY RISKS in the RFP from a bidder's perspective.

This agent flags things that make delivery harder:
  - Unrealistic timelines
  - Scope that is unusually large or complex
  - Contractual penalties or SLAs that are hard to meet
  - Technology constraints imposed by the client
  - Integration complexity
  - Data migration requirements
  - Unclear ownership / governance
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import structlog
from agents.base import call_claude
from core.schemas import Category, DocumentChunk, Requirement

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext

log = structlog.get_logger()

SYSTEM_PROMPT = """You are a delivery risk analyst reviewing an RFP on behalf of a bidding vendor.

Identify DELIVERY RISKS — things that make it harder or riskier to successfully deliver the project:

Risk types to look for:
1. TIMELINE: Aggressive or fixed go-live dates with large scope
2. SCOPE CREEP: Open-ended language ("and other modules as required")
3. TECHNICAL COMPLEXITY: Legacy system integrations, unusual tech stack mandates, large data migrations
4. SLA / PENALTY RISK: Uptime commitments, liquidated damages, penalty clauses that are hard to meet
5. DEPENDENCY: Risks dependent on the client (e.g. "client will provide test data within 2 weeks")
6. GOVERNANCE: Unclear decision-making authority, too many approval layers
7. RESOURCE: Requires rare skills or certifications the average vendor may not have
8. DATA: Large volume migrations, complex transformations, or unspecified legacy data quality

For each risk found, output a JSON array:
[
  {
    "title": "Short risk label",
    "description": "What the risk is, why it matters, and what could go wrong",
    "source_section": "Section heading",
    "priority": "must | should | could",
    "confidence": 0.9,
    "ambiguity_flag": false,
    "clarification_question": "Optional — question to ask if the risk stems from ambiguity",
    "raw_excerpt": "Exact text that triggered this risk"
  }
]

RULES:
- Focus on DELIVERY risk from the bidder's perspective, not business risk to the client
- Be specific — "tight timeline" is not useful; "6-month timeline for 15 modules including data migration" is
- Return [] if the chunk contains nothing risky
- Output ONLY valid JSON. No preamble."""


def extract_risks(
    chunks: list[DocumentChunk],
    id_start: int = 1,
    org_context: Optional[OrganizationContext] = None,
) -> list[Requirement]:
    """
    Extract risk items from all document chunks.
    
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
                    category=Category.RISK,
                    page_ref=str(chunk.page),
                    **_sanitise(item),
                )
                requirements.append(req)
                counter += 1
            except Exception as exc:  # noqa: BLE001
                log.warning("risk_parse_error", error=str(exc))

    log.info("risk_extraction_done", count=len(requirements))
    return requirements


def _generate_requirement_id(counter: int, org_context: Optional[OrganizationContext]) -> str:
    """Generate requirement ID using organizational context naming conventions."""
    if not org_context:
        return f"RSK-{counter:03d}"
    
    prefix = org_context.naming_conventions.risk_prefix
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
    priority_map = {"must": "must", "should": "should", "could": "could", "wont": "wont"}
    clean["priority"] = priority_map.get(raw_priority, "should")
    conf = clean.get("confidence", 0.9)
    try:
        clean["confidence"] = max(0.0, min(1.0, float(conf)))
    except (TypeError, ValueError):
        clean["confidence"] = 0.9
    return clean
