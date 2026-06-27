"""
agents/nonfunctional.py
-----------------------
Extracts NON-FUNCTIONAL requirements (NFRs) from RFP chunks.

NFRs answer: "How well must the system perform?"
Examples: response time, uptime SLA, concurrent users, encryption standards,
          browser support, data retention, disaster recovery RTO/RPO.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import structlog
from agents.base import call_claude
from core.schemas import Category, DocumentChunk, Requirement

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext

log = structlog.get_logger()

SYSTEM_PROMPT = """You are a solutions architect specialising in extracting NON-FUNCTIONAL requirements (NFRs) from RFP documents.

NON-FUNCTIONAL requirements define HOW WELL the system must perform:

Categories to look for:
- PERFORMANCE: response time, throughput, latency, load capacity
- AVAILABILITY / RELIABILITY: uptime SLA, MTTR, failover, redundancy
- SCALABILITY: concurrent users, data volume growth, horizontal scaling
- SECURITY: encryption (at rest, in transit), authentication methods, vulnerability scanning
- USABILITY: accessibility standards (WCAG), browser/device support, language localisation
- MAINTAINABILITY: code coverage, deployment frequency, rollback capability
- DATA: retention periods, backup frequency, RPO/RTO
- INTEROPERABILITY: API standards (REST, GraphQL), data formats (JSON, XML)

SPECIAL NOTE ON TABLES:
When you encounter text marked with [TABLE DATA]...[END TABLE], this is structured tabular information.
Pay special attention to:
- SLA tables (uptime, response time, support hours)
- Resource allocation tables (capacity, limits, thresholds)
- Timeline and milestone tables
- Compliance and certification requirements
Extract each meaningful row as a separate requirement if applicable. Include table data in your raw_excerpt.

Output a JSON array of objects with EXACTLY these fields:
[
  {
    "title": "Short label, max 10 words",
    "description": "Precise, measurable description. Include specific numbers/thresholds when stated.",
    "source_section": "Section heading",
    "priority": "must | should | could | wont",
    "confidence": 0.95,
    "ambiguity_flag": false,
    "clarification_question": null,
    "raw_excerpt": "Exact source text"
  }
]

IMPORTANT RULES:
- Prefer MEASURABLE descriptions: "API response time under 200ms at p95" over "system must be fast"
- If a number is stated (e.g. "99.9% uptime"), include it verbatim in description
- If performance is mentioned vaguely without a metric, set ambiguity_flag=true
- Return [] if no NFRs are present in the chunk
- Output ONLY valid JSON. No preamble."""

NFR_ID_PREFIX = "NFR"


def extract_nonfunctional(
    chunks: list[DocumentChunk],
    id_start: int = 1,
    org_context: Optional[OrganizationContext] = None,
) -> list[Requirement]:
    """
    Extract non-functional requirements from all document chunks.
    
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
                    category=Category.NON_FUNCTIONAL,
                    page_ref=str(chunk.page),
                    **_sanitise(item),
                )
                requirements.append(req)
                counter += 1
            except Exception as exc:  # noqa: BLE001
                log.warning("nfr_parse_error", error=str(exc))

    log.info("nfr_extraction_done", count=len(requirements))
    return requirements


def _generate_requirement_id(counter: int, org_context: Optional[OrganizationContext]) -> str:
    """Generate requirement ID using organizational context naming conventions."""
    if not org_context:
        return f"{NFR_ID_PREFIX}-{counter:03d}"
    
    prefix = org_context.naming_conventions.non_functional_prefix
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
