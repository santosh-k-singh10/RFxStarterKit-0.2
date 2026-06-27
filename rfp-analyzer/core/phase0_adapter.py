"""
core/phase0_adapter.py
----------------------
Bridges the Phase 0 DocumentContext (document-consolidator) to the
RFP Analyzer's native List[DocumentChunk] format.

Phase 0 output shape
---------------------
  DocumentContext.phase_contexts["phase1"].chunks  → List[Chunk]
  Chunk.content          : str  (section text)
  Chunk.source_document  : str  (original filename)
  Chunk.section_type     : SectionType (enum)
  Chunk.page_ref         : str  e.g. "p.4-5"
  Chunk.conflict_flag    : bool
  Chunk.conflict_ref     : Optional[str]  (conflict_id)

RFP Analyzer expected shape
-----------------------------
  DocumentChunk.section    : str  (heading label shown in results)
  DocumentChunk.text       : str  (body used by agents)
  DocumentChunk.page       : int  (first page number)
  DocumentChunk.char_count : int  (auto-derived)
"""

from __future__ import annotations

import logging
import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Tuple

from core.schemas import DocumentChunk

# Phase 0 package lives in document-consolidator/phase0_router/
_PHASE0_PATH = Path(__file__).parent.parent.parent / "document-consolidator" / "phase0_router"

if TYPE_CHECKING:
    from phase0.schema import DocumentContext  # type: ignore[import]

log = logging.getLogger(__name__)


def _ensure_phase0_on_path() -> bool:
    """Add Phase 0 package directory to sys.path once."""
    target = str(_PHASE0_PATH)
    if not Path(target).exists():
        log.warning("phase0_package_not_found", path=target)
        return False
    if target not in sys.path:
        sys.path.insert(0, target)
    return True


def is_phase0_available() -> bool:
    """Return True if the Phase 0 package is importable."""
    if not _ensure_phase0_on_path():
        return False
    try:
        import phase0.router  # noqa: F401
        return True
    except ImportError:
        return False


def run_phase0(file_paths: list[str]) -> "DocumentContext | None":
    """
    Execute the Phase 0 pipeline over a list of uploaded file paths.

    Returns a DocumentContext on success, None on failure (caller should fall
    back to standard ingestion).
    """
    if not _ensure_phase0_on_path():
        return None

    try:
        from phase0.router import Phase0Router  # type: ignore[import]
    except ImportError as exc:
        log.warning("phase0_import_error", error=str(exc))
        return None

    try:
        router = Phase0Router()
        doc_context = router.run(file_paths)
        log.info(
            "phase0_complete",
            rfp_id=doc_context.rfp_id,
            docs=len(doc_context.documents),
            conflicts=len(doc_context.conflicts),
        )
        return doc_context
    except Exception as exc:
        log.error("phase0_pipeline_error", error=str(exc))
        return None


def _parse_page(page_ref: str) -> int:
    """
    Extract the first integer from a page reference like "p.4-5" or "12".
    Falls back to 1 on any parse failure.
    """
    match = re.search(r"\d+", page_ref or "")
    return int(match.group()) if match else 1


def adapt_to_analyzer_chunks(
    doc_context: "DocumentContext",
    phase_target: str = "phase1",
) -> Tuple[list[DocumentChunk], dict]:
    """
    Convert a Phase 0 DocumentContext into the format expected by the
    RFP Analyzer agents.

    Parameters
    ----------
    doc_context:
        Output of Phase0Router.run().
    phase_target:
        Which phase slice to extract.  Defaults to "phase1" (the RFP
        requirement extraction phase).

    Returns
    -------
    chunks : list[DocumentChunk]
        Ready to be handed to extract_functional(), extract_nonfunctional(), …
    metadata : dict
        Phase 0 provenance info to store in job metadata.
    """
    phase_ctx = doc_context.phase_contexts.get(phase_target)
    if not phase_ctx:
        # Graceful fallback: merge ALL available chunks across phases
        log.warning(
            "phase0_target_not_found",
            target=phase_target,
            available=list(doc_context.phase_contexts.keys()),
        )
        all_p0_chunks = [
            ch
            for ctx in doc_context.phase_contexts.values()
            for ch in ctx.chunks
        ]
    else:
        all_p0_chunks = phase_ctx.chunks

    analyzer_chunks: list[DocumentChunk] = []
    for p0 in all_p0_chunks:
        # Build a descriptive section label
        section_label = (
            f"{p0.source_document} › {p0.section_type.value.replace('_', ' ').title()}"
        )

        # Prepend a conflict warning so agents can flag the requirement
        body = p0.content
        if p0.conflict_flag and p0.conflict_ref:
            body = (
                f"⚠️ CONFLICT WARNING [{p0.conflict_ref}]: "
                f"This section conflicts with another document.\n\n{body}"
            )

        chunk = DocumentChunk(
            section=section_label,
            text=body,
            page=_parse_page(p0.page_ref),
            char_count=len(body),
        )
        analyzer_chunks.append(chunk)

    # Build provenance metadata
    metadata: dict = {
        "phase0_rfp_id": doc_context.rfp_id,
        "phase0_docs": [
            {
                "filename": d.filename,
                "doc_type": d.doc_type.value,
                "confidence": d.confidence,
                "needs_review": d.needs_review,
            }
            for d in doc_context.documents
        ],
        "phase0_conflicts": [
            {
                "conflict_id": c.conflict_id,
                "severity": c.severity,
                "description": c.description,
                "source_documents": c.source_documents,
            }
            for c in doc_context.conflicts
        ],
        "phase0_chunk_count": len(analyzer_chunks),
        "phase0_conflict_count": len(doc_context.conflicts),
        "phase0_docs_needing_review": doc_context.metadata.get(
            "docs_needing_review", []
        ),
    }

    log.info(
        "phase0_adapter_complete",
        chunks=len(analyzer_chunks),
        conflicts=len(doc_context.conflicts),
    )
    return analyzer_chunks, metadata
