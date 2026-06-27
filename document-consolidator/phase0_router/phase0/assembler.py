"""
phase0/assembler.py
Context Assembler — builds the final DocumentContext output from classified docs + chunks + conflicts.

Responsibilities:
- Groups chunks by phase_relevance into per-phase PhaseContext objects
- Deduplicates overlapping chunks (same content appearing from multiple docs)
- Estimates token count per phase context (for downstream context window budgeting)
- Assembles the final DocumentContext with metadata summary
"""

from __future__ import annotations
import hashlib
import logging
from typing import List, Dict

from .schema import (
    ClassifiedDocument, Chunk, Conflict,
    PhaseContext, PhaseTarget, DocumentContext,
)
from .utils import estimate_tokens

logger = logging.getLogger(__name__)

# If two chunks share more than this fraction of content, treat as duplicate
DEDUP_SIMILARITY_THRESHOLD = 0.85


class ContextAssembler:
    """
    Assembles the final DocumentContext from all Phase 0 sub-agent outputs.
    """

    def assemble(
        self,
        documents: List[ClassifiedDocument],
        all_chunks: List[Chunk],
        conflicts: List[Conflict],
    ) -> DocumentContext:
        """
        Main entry point.

        Args:
            documents: classifier output (one per uploaded file)
            all_chunks: all chunks from all documents (post conflict-detection mutation)
            conflicts: conflict detector output

        Returns:
            DocumentContext — the Phase 0 output contract
        """
        logger.info(
            f"Assembling context: {len(documents)} docs, "
            f"{len(all_chunks)} chunks, {len(conflicts)} conflicts"
        )

        phase_contexts = self._build_phase_contexts(all_chunks)
        metadata = self._build_metadata(documents, all_chunks, conflicts, phase_contexts)

        return DocumentContext(
            documents=documents,
            phase_contexts={k.value: v for k, v in phase_contexts.items()},
            conflicts=conflicts,
            metadata=metadata,
        )

    def _build_phase_contexts(
        self, all_chunks: List[Chunk]
    ) -> Dict[PhaseTarget, PhaseContext]:
        """
        Groups chunks by phase_relevance. Chunks tagged ALL go into every phase.
        Deduplicates within each phase bucket.
        """
        buckets: Dict[PhaseTarget, List[Chunk]] = {
            PhaseTarget.PHASE1: [],
            PhaseTarget.PHASE2: [],
            PhaseTarget.PHASE3: [],
        }

        for chunk in all_chunks:
            targets = chunk.phase_relevance
            # Expand ALL to every concrete phase
            if PhaseTarget.ALL in targets:
                targets = [PhaseTarget.PHASE1, PhaseTarget.PHASE2, PhaseTarget.PHASE3]

            for target in targets:
                if target in buckets:
                    buckets[target].append(chunk)

        phase_contexts: Dict[PhaseTarget, PhaseContext] = {}
        for phase, chunks in buckets.items():
            deduped = self._deduplicate(chunks)
            token_estimate = sum(estimate_tokens(c.content) for c in deduped)
            phase_contexts[phase] = PhaseContext(
                phase=phase,
                chunks=deduped,
                total_tokens_estimate=token_estimate,
            )
            logger.info(
                f"Phase context {phase.value}: "
                f"{len(deduped)} chunks, ~{token_estimate} tokens"
            )

        return phase_contexts

    def _deduplicate(self, chunks: List[Chunk]) -> List[Chunk]:
        """
        Removes near-duplicate chunks based on content fingerprint.
        Keeps the first occurrence (from the highest-confidence document, since
        classifier runs in order).
        """
        seen_hashes: set[str] = set()
        unique: List[Chunk] = []

        for chunk in chunks:
            # Fingerprint: hash of normalised content (lowercase, collapsed whitespace)
            normalised = " ".join(chunk.content.lower().split())
            # Use first 500 chars for fingerprint to catch overlapping windows
            fingerprint = hashlib.md5(normalised[:500].encode()).hexdigest()

            if fingerprint not in seen_hashes:
                seen_hashes.add(fingerprint)
                unique.append(chunk)

        removed = len(chunks) - len(unique)
        if removed:
            logger.debug(f"Deduplication removed {removed} near-duplicate chunks")

        return unique

    def _build_metadata(
        self,
        documents: List[ClassifiedDocument],
        all_chunks: List[Chunk],
        conflicts: List[Conflict],
        phase_contexts: Dict[PhaseTarget, PhaseContext],
    ) -> dict:
        docs_needing_review = [d.filename for d in documents if d.needs_review]

        return {
            "total_docs": len(documents),
            "total_chunks": len(all_chunks),
            "conflict_count": len(conflicts),
            "docs_needing_review": docs_needing_review,
            "phase_token_estimates": {
                phase.value: ctx.total_tokens_estimate
                for phase, ctx in phase_contexts.items()
            },
            "doc_types_found": list({d.doc_type.value for d in documents}),
        }
