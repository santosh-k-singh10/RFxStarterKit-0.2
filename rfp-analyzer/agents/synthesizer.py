"""
agents/synthesizer.py
---------------------
Synthesis stage: takes all raw requirements from every agent and:

1. Deduplicates — removes near-identical items (same title after normalisation)
2. Cross-links — asks Claude to identify relationships between requirements
   (e.g. a GDPR compliance req that implies a data-retention NFR)
3. RAG verification — optionally checks each requirement is grounded in source text
4. Sorts — by category then priority then ID

This runs after all parallel agents complete.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
import json
import structlog

from agents.base import call_claude
from core.schemas import Category, Priority, Requirement

if TYPE_CHECKING:
    from org_context.context_schema import OrganizationContext
    from core.embedder import DocumentIndex

log = structlog.get_logger()

# Priority sort order (lower = higher priority)
_PRIORITY_ORDER = {
    Priority.MUST: 0,
    Priority.SHOULD: 1,
    Priority.COULD: 2,
    Priority.WONT: 3,
}

_CATEGORY_ORDER = {
    Category.FUNCTIONAL: 0,
    Category.NON_FUNCTIONAL: 1,
    Category.COMPLIANCE: 2,
    Category.AMBIGUITY: 3,
    Category.RISK: 4,
}


def synthesize(
    requirements: list[Requirement],
    document_index: Optional["DocumentIndex"] = None,
    org_context: Optional["OrganizationContext"] = None,
) -> list[Requirement]:
    """
    Main synthesis entry point.

    Parameters
    ----------
    requirements : list[Requirement]
        Combined output from all 5 sub-agents.
    document_index : DocumentIndex | None
        If provided, runs RAG-based grounding verification.
    org_context : Optional[OrganizationContext]
        Organizational context for context-aware post-processing.

    Returns
    -------
    list[Requirement]
        Deduplicated, cross-linked, sorted requirements.
    """
    if not requirements:
        return []

    log.info("synthesis_start", total_raw=len(requirements))

    # Step 1: Deduplicate
    deduped = _deduplicate(requirements)
    log.info("after_dedup", count=len(deduped))

    # Step 2: RAG verification (optional)
    if document_index is not None:
        deduped = document_index.flag_ungrounded(deduped)

    # Step 3: Cross-link related requirements
    deduped = _cross_link(deduped)

    # Step 4: Sort
    deduped.sort(key=lambda r: (
        _CATEGORY_ORDER.get(r.category, 9),
        _PRIORITY_ORDER.get(r.priority, 9),
        r.id,
    ))

    log.info("synthesis_done", final_count=len(deduped))
    return deduped


# ─────────────────────────────────────────────────────────────────────────────
# Deduplication
# ─────────────────────────────────────────────────────────────────────────────

def _normalise_title(title: str) -> str:
    """Lower-case, strip punctuation, collapse whitespace."""
    import re
    title = title.lower()
    # Keep logical separation for hyphenated words (e.g. Aadhaar-based -> Aadhaar based)
    title = re.sub(r'[-_]', ' ', title)
    title = re.sub(r'[^(\w\s)]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def _deduplicate(requirements: list[Requirement]) -> list[Requirement]:
    """
    Keep one requirement per normalised title.
    When duplicates exist, keep the one with higher confidence.
    """
    seen: dict[tuple[str, str], Requirement] = {}

    for req in requirements:
        key = (_normalise_title(req.title), req.category.value)
        if key not in seen:
            seen[key] = req
        else:
            existing = seen[key]
            if req.confidence > existing.confidence:
                seen[key] = req

    return list(seen.values())


# ─────────────────────────────────────────────────────────────────────────────
# Cross-linking
# ─────────────────────────────────────────────────────────────────────────────

_CROSSLINK_SYSTEM = """You are a requirements analyst identifying relationships between requirements.

Given a list of requirements (id + title + category), identify pairs that are RELATED:
- A compliance requirement that implies a non-functional constraint
- A functional requirement that depends on another functional requirement
- A risk that is caused by an ambiguity
- A non-functional requirement that constrains how a functional one is implemented

Return a JSON array of relationship pairs:
[
  {"id1": "CR-001", "id2": "NFR-005", "reason": "GDPR data retention implies specific backup NFR"},
  {"id1": "FR-012", "id2": "FR-003",  "reason": "Reporting module depends on data ingestion module"}
]

If no meaningful relationships exist, return [].
Output ONLY valid JSON."""


def _cross_link(requirements: list[Requirement]) -> list[Requirement]:
    """Ask Claude to identify related requirement pairs and populate related_ids."""
    if len(requirements) < 2:
        return requirements

    summaries = [
        {"id": r.id, "title": r.title, "category": r.category.value}
        for r in requirements
    ]

    items = call_claude(
        system_prompt=_CROSSLINK_SYSTEM,
        user_content=json.dumps(summaries, indent=2),
        max_tokens=8192,  # Increased for extended thinking models
    )

    id_map = {r.id: r for r in requirements}

    for link in items:
        id1 = link.get("id1", "")
        id2 = link.get("id2", "")
        if id1 in id_map and id2 in id_map:
            if id2 not in id_map[id1].related_ids:
                id_map[id1].related_ids.append(id2)
            if id1 not in id_map[id2].related_ids:
                id_map[id2].related_ids.append(id1)

    return requirements