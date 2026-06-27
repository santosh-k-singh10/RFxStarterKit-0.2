"""
phase0/router.py
Phase0Router — orchestrates all sub-agents in sequence.

Pipeline:
1. ClassifierAgent  → ClassifiedDocument per file
2. ChunkerAgent     → List[Chunk] per document
3. ConflictDetectorAgent → List[Conflict], mutates chunk flags
4. ContextAssembler → DocumentContext (final output)
"""

from __future__ import annotations
import logging
from pathlib import Path
from typing import List, Optional

from .llm_client import get_anthropic_client
from .classifier import ClassifierAgent
from .chunker import ChunkerAgent
from .conflict_detector import ConflictDetectorAgent
from .assembler import ContextAssembler
from .schema import DocumentContext, ClassifiedDocument, Chunk

logger = logging.getLogger(__name__)


class Phase0Router:
    """
    Top-level orchestrator for Phase 0.
    Accepts a list of file paths, returns a DocumentContext.
    """

    def __init__(self, client = None):
        """
        Initialize Phase0Router with an LLM client.
        
        Args:
            client: Optional Anthropic client. If None, will use get_anthropic_client()
                   which supports both OpenAI-compatible API and direct Anthropic API.
        """
        self.client = client if client is not None else get_anthropic_client()
        self.classifier = ClassifierAgent(self.client)
        self.chunker = ChunkerAgent(self.client)
        self.conflict_detector = ConflictDetectorAgent(self.client)
        self.assembler = ContextAssembler()

    def run(self, filepaths: List[str | Path]) -> DocumentContext:
        """
        Synchronous pipeline execution.

        Args:
            filepaths: list of paths to uploaded documents

        Returns:
            DocumentContext consumed by Phase 1–3
        """
        logger.info(f"Phase 0 start — {len(filepaths)} document(s)")

        # Step 1: Classify all documents
        classified_docs: List[ClassifiedDocument] = []
        for fp in filepaths:
            doc = self.classifier.classify(fp)
            classified_docs.append(doc)

        # Step 2: Chunk all documents
        all_chunks: List[Chunk] = []
        for doc in classified_docs:
            chunks = self.chunker.chunk(doc)
            all_chunks.extend(chunks)

        logger.info(f"Total chunks produced: {len(all_chunks)}")

        # Step 3: Detect conflicts (mutates chunk flags in place)
        conflicts = self.conflict_detector.detect(all_chunks)

        # Step 4: Assemble final DocumentContext
        doc_context = self.assembler.assemble(classified_docs, all_chunks, conflicts)

        logger.info(
            f"Phase 0 complete — rfp_id={doc_context.rfp_id}, "
            f"conflicts={len(conflicts)}, "
            f"docs_for_review={doc_context.metadata.get('docs_needing_review', [])}"
        )
        return doc_context
