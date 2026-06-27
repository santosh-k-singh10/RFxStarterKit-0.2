"""
agents/ambiguity.py
-------------------
Identifies AMBIGUITIES, GAPS, and items needing clarification in the RFP.

This agent does NOT extract requirements — it generates a list of
clarification questions that the bidder should raise with the issuer.

Examples:
  - "User-friendly interface" — what usability standard applies?
  - "Industry-standard security" — which standard exactly?
  - Contradictions between two sections
  - Missing information (e.g. expected user count not stated)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import structlog
from agents.base import call_claude
from core.schemas import Category, DocumentChunk, Requirement

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext

log = structlog.get_logger()

SYSTEM_PROMPT = """You are an experienced RFP reviewer identifying AMBIGUITIES, GAPS, and CONTRADICTIONS in RFP documents.

Your job is NOT to extract requirements — it is to find places where the RFP is:
1. VAGUE: Uses undefined terms like "user-friendly", "fast", "industry-standard", "modern"
2. INCOMPLETE: Missing critical information (e.g. expected user count, data volumes, go-live date)
3. CONTRADICTORY: Two statements that cannot both be true
4. UNDEFINED SCOPE: "and other features as required" — open-ended scope creep language
5. ASSUMPTION-HEAVY: Statements that assume the reader shares context that is not stated

For each issue found, output a JSON array:
[
  {
    "title": "Short label of the ambiguity",
    "description": "What is vague or missing and why it matters for delivery",
    "source_section": "Section heading",
    "priority": "must",
    "confidence": 1.0,
    "ambiguity_flag": true,
    "clarification_question": "The specific question the bidder should ask the issuer",
    "raw_excerpt": "The exact vague or incomplete text"
  }
]

RULES:
- Every item MUST have ambiguity_flag: true
- Every item MUST have a clarification_question — make it specific and actionable
- Do not flag things that are clearly and completely stated
- Return [] if the chunk is well-specified with no ambiguities
- Output ONLY valid JSON. No preamble."""


def extract_ambiguities(
    chunks: list[DocumentChunk],
    id_start: int = 1,
    org_context: Optional[OrganizationContext] = None,
) -> list[Requirement]:
    """
    Extract ambiguities and clarification needs from all document chunks.
    
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
    
    log.info("ambiguity_agent_processing_chunks", total_chunks=len(chunks))

    for idx, chunk in enumerate(chunks, 1):
        if not chunk.is_substantial():
            log.debug("ambiguity_skipping_small_chunk", chunk_idx=idx)
            continue

        log.debug("ambiguity_processing_chunk", chunk_idx=idx, section=chunk.section)
        
        user_content = (
            f"Section: {chunk.section}\n"
            f"Page: {chunk.page}\n\n"
            f"{chunk.text}"
        )

        items = call_claude(SYSTEM_PROMPT, user_content, org_context=org_context)
        
        if not items:
            log.debug("ambiguity_no_items_found", chunk_idx=idx, section=chunk.section)

        for item in items:
            try:
                # Force ambiguity fields to be correct
                item["ambiguity_flag"] = True
                item["priority"] = "must"

                req_id = _generate_requirement_id(counter, org_context)
                req = Requirement(
                    id=req_id,
                    category=Category.AMBIGUITY,
                    page_ref=str(chunk.page),
                    **_sanitise(item),
                )
                requirements.append(req)
                counter += 1
            except Exception as exc:  # noqa: BLE001
                log.warning("ambiguity_parse_error", error=str(exc), chunk_idx=idx)

    log.info("ambiguity_extraction_done", count=len(requirements))
    return requirements


def _generate_requirement_id(counter: int, org_context: Optional[OrganizationContext]) -> str:
    """Generate requirement ID using organizational context naming conventions."""
    if not org_context:
        return f"AMB-{counter:03d}"
    
    prefix = org_context.naming_conventions.ambiguity_prefix
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
    conf = clean.get("confidence", 1.0)
    try:
        clean["confidence"] = max(0.0, min(1.0, float(conf)))
    except (TypeError, ValueError):
        clean["confidence"] = 1.0
    return clean
