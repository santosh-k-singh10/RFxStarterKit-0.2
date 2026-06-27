"""
agents/functional.py
--------------------
Extracts FUNCTIONAL requirements from RFP document chunks.

Functional requirements answer: "What must the system DO?"
Examples: user login, data export, search functionality, API integration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import structlog
from agents.base import call_claude
from core.schemas import Category, DocumentChunk, Priority, Requirement

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext

log = structlog.get_logger()

SYSTEM_PROMPT = """You are a senior business analyst specialising in extracting FUNCTIONAL requirements from RFP (Request for Proposal) documents.

FUNCTIONAL requirements describe WHAT the system must DO:
- Features and capabilities users can interact with
- Business workflows and processes the system must support
- Data operations: create, read, update, delete, import, export
- Integrations with external systems or APIs
- User roles and access control
- Notifications, reporting, dashboards

SPECIAL NOTE ON TABLES:
When you encounter text marked with [TABLE DATA]...[END TABLE], this is structured tabular information.
Pay special attention to:
- Resource requirements (roles, quantities, skills, FTEs)
- Technical specifications and configurations
- Feature lists with details
- Staffing and team composition
Extract each meaningful row as a separate requirement if applicable. Include table data in your raw_excerpt.

For every functional requirement you find, output a JSON array of objects with EXACTLY these fields:
[
  {
    "title": "Short label, max 10 words",
    "description": "Clear, implementation-neutral description of what is required. One to three sentences.",
    "source_section": "The section heading this was found in",
    "priority": "must | should | could | wont",
    "confidence": 0.95,
    "ambiguity_flag": false,
    "clarification_question": null,
    "raw_excerpt": "The exact sentence(s) from the input that led to this requirement"
  }
]

PRIORITY MAPPING:
- "shall", "must", "is required", "mandatory" → "must"
- "should", "is expected" → "should"
- "may", "can", "optionally" → "could"
- "will not", "out of scope" → "wont"

CONFIDENCE SCORING:
- 1.0 = Explicitly stated with clear scope
- 0.8 = Clearly implied but not word-for-word stated
- 0.6 = Inferred from context — mark ambiguity_flag=true
- Below 0.6 = Do not extract

RULES:
- Extract only what is present in the text. Do NOT invent requirements.
- If a requirement is vague (e.g. "user-friendly interface"), set ambiguity_flag=true and write a clarification_question.
- If nothing functional is found in the chunk, return an empty array: []
- Output ONLY valid JSON. No preamble, no explanation, no markdown headers."""


def extract_functional(
    chunks: list[DocumentChunk],
    id_start: int = 1,
    org_context: Optional[OrganizationContext] = None,
) -> list[Requirement]:
    """
    Run the functional agent over all document chunks.

    Parameters
    ----------
    chunks : list[DocumentChunk]
        Section-aware chunks from the ingested document.
    id_start : int
        Starting ID counter (e.g. pass 100 if you want FR-100, FR-101 ...).
    org_context : Optional[OrganizationContext]
        Organizational context for context-aware extraction.
        If not provided, will attempt to load from context manager.

    Returns
    -------
    list[Requirement]
        All functional requirements found, with IDs assigned sequentially.
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

        # Pass org_context to call_claude
        items = call_claude(SYSTEM_PROMPT, user_content, org_context=org_context)

        for item in items:
            try:
                # Generate context-aware requirement ID
                req_id = _generate_requirement_id(counter, org_context)
                
                req = Requirement(
                    id=req_id,
                    category=Category.FUNCTIONAL,
                    page_ref=str(chunk.page),
                    **_sanitise(item),
                )
                requirements.append(req)
                counter += 1
            except Exception as exc:  # noqa: BLE001
                log.warning("functional_req_parse_error", error=str(exc), item=item)

    log.info("functional_extraction_done", count=len(requirements))
    return requirements


def _generate_requirement_id(counter: int, org_context: Optional[OrganizationContext]) -> str:
    """
    Generate requirement ID using organizational context naming conventions.
    
    Parameters
    ----------
    counter : int
        Sequential counter for the requirement
    org_context : Optional[OrganizationContext]
        Organizational context with naming conventions
        
    Returns
    -------
    str
        Formatted requirement ID (e.g., "FR-001" or "FR-HC-001")
    """
    if not org_context:
        # Fallback to default naming
        return f"FR-{counter:03d}"
    
    # Use organization's naming conventions
    prefix = org_context.naming_conventions.functional_prefix
    separator = org_context.naming_conventions.separator
    padding = org_context.naming_conventions.padding
    
    return f"{prefix}{separator}{counter:0{padding}d}"


def _sanitise(item: dict) -> dict:
    """Remove unknown fields and normalise priority."""
    allowed = {
        "title", "description", "source_section",
        "priority", "confidence", "ambiguity_flag",
        "clarification_question", "raw_excerpt",
    }
    clean = {k: v for k, v in item.items() if k in allowed}

    # Normalise priority to enum values
    raw_priority = str(clean.get("priority", "must")).lower().strip()
    priority_map = {"must": "must", "should": "should", "could": "could", "wont": "wont", "won't": "wont"}
    clean["priority"] = priority_map.get(raw_priority, "must")

    # Clamp confidence
    conf = clean.get("confidence", 0.9)
    try:
        clean["confidence"] = max(0.0, min(1.0, float(conf)))
    except (TypeError, ValueError):
        clean["confidence"] = 0.9

    return clean
