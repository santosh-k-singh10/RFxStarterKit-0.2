"""
phase0/chunker.py
Chunker Agent — splits each classified document into semantically coherent sections.

Each chunk gets:
- section_type  : what kind of content it is
- phase_relevance: which downstream phases need it
- page_ref      : approximate page location for traceability
- chunk_id      : stable unique id carried through to Phase 1+ outputs

Strategy:
- Splits text into overlapping windows (~1500 chars with 200 char overlap)
- Sends each window to Claude asking for section_type classification
- Assigns phase_relevance based on section_type using a static routing table
- Batches windows to minimise LLM calls where possible
"""

from __future__ import annotations
import json
import logging
import re
from typing import List

from .schema import (
    Chunk, ClassifiedDocument, DocType,
    SectionType, PhaseTarget,
)
from .utils import estimate_tokens, page_ref_from_char_offset

logger = logging.getLogger(__name__)

# Chunk sizing
CHUNK_SIZE_CHARS  = 1500
CHUNK_OVERLAP     = 200
MAX_CHUNKS_PER_DOC = 80   # safety cap

# Static routing table: section_type → which phases receive this chunk
PHASE_ROUTING: dict[SectionType, List[PhaseTarget]] = {
    SectionType.FUNCTIONAL_REQUIREMENT:     [PhaseTarget.PHASE1, PhaseTarget.PHASE2],
    SectionType.NON_FUNCTIONAL_REQUIREMENT: [PhaseTarget.PHASE1, PhaseTarget.PHASE2],
    SectionType.ARCHITECTURE_NOTE:          [PhaseTarget.PHASE2],
    SectionType.TIMELINE:                   [PhaseTarget.PHASE3],
    SectionType.PRICING:                    [PhaseTarget.PHASE3],
    SectionType.COMPLIANCE_CLAUSE:          [PhaseTarget.PHASE1],
    SectionType.SCOPE:                      [PhaseTarget.PHASE1, PhaseTarget.PHASE2, PhaseTarget.PHASE3],
    SectionType.ASSUMPTION:                 [PhaseTarget.PHASE1, PhaseTarget.PHASE3],
    SectionType.GLOSSARY:                   [PhaseTarget.ALL],
    SectionType.GENERAL:                    [PhaseTarget.ALL],
}


SECTION_CLASSIFY_PROMPT = """You are classifying a chunk of text from an RFP document.

Document type: {doc_type}

Classify this text chunk into exactly ONE section type:
- functional_requirement      : specific system features or capabilities required
- non_functional_requirement  : performance, security, scalability, availability requirements
- timeline                    : project milestones, deadlines, delivery schedules
- pricing                     : costs, pricing tables, commercial terms
- compliance_clause           : regulatory, legal, security compliance requirements
- architecture_note           : technical architecture, tech stack, design patterns
- scope                       : project scope, in-scope / out-of-scope items
- assumption                  : stated assumptions or dependencies
- glossary                    : definitions, abbreviations
- general                     : introductory or general context not fitting above

Respond ONLY with a JSON object (no markdown, no explanation):
{{
  "section_type": "<type>",
  "confidence": <float 0.0-1.0>
}}

Text chunk:
---
{text}
---"""


class ChunkerAgent:
    """
    Splits a ClassifiedDocument into Chunks with section_type and phase_relevance.
    """

    def __init__(self, client = None):
        """
        Initialize ChunkerAgent with an LLM client.
        
        Args:
            client: Anthropic client or OpenAI-compatible wrapper. If None, uses get_anthropic_client().
        """
        if client is None:
            from .llm_client import get_anthropic_client
            client = get_anthropic_client()
        self.client = client

    def chunk(self, doc: ClassifiedDocument) -> List[Chunk]:
        """
        Main entry. Splits doc.raw_text into chunks and classifies each.

        Returns:
            List[Chunk] with all metadata populated
        """
        logger.info(f"Chunking: {doc.filename} ({len(doc.raw_text)} chars)")

        windows = self._split_into_windows(doc.raw_text)
        if len(windows) > MAX_CHUNKS_PER_DOC:
            logger.warning(
                f"{doc.filename}: {len(windows)} windows exceeds cap {MAX_CHUNKS_PER_DOC}. Truncating."
            )
            windows = windows[:MAX_CHUNKS_PER_DOC]

        chunks: List[Chunk] = []
        for i, (text, char_offset) in enumerate(windows):
            section_type = self._classify_section(text, doc.doc_type)
            phase_relevance = PHASE_ROUTING.get(section_type, [PhaseTarget.ALL])
            page_ref = page_ref_from_char_offset(char_offset)

            chunk = Chunk(
                source_document=doc.filename,
                page_ref=page_ref,
                doc_type=doc.doc_type,
                section_type=section_type,
                phase_relevance=phase_relevance,
                content=text,
            )
            chunks.append(chunk)

        logger.info(f"{doc.filename} → {len(chunks)} chunks")
        return chunks

    def _split_into_windows(self, text: str) -> List[tuple[str, int]]:
        """
        Splits text into overlapping windows.
        Returns list of (window_text, char_offset_in_original).
        """
        windows = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = min(start + CHUNK_SIZE_CHARS, text_len)
            window = text[start:end].strip()
            if window:
                windows.append((window, start))
            if end >= text_len:
                break
            start = end - CHUNK_OVERLAP  # overlap with previous window

        return windows

    def _classify_section(self, text: str, doc_type: DocType) -> SectionType:
        """
        Calls LLM to classify a text window into a SectionType.
        Falls back to GENERAL on any error.
        """
        prompt = SECTION_CLASSIFY_PROMPT.format(
            doc_type=doc_type.value,
            text=text[:1200],  # keep prompt tight
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=128,
                messages=[{"role": "user", "content": prompt}],
            )
            # Support both anthropic.types.TextBlock and our ContentBlock wrapper
            first_block = response.content[0]
            if hasattr(first_block, "text"):
                content = first_block.text.strip()
            else:
                logger.error(f"Unexpected content block type: {type(first_block)}")
                return SectionType.GENERAL
            return self._parse_section_type(content)

        except Exception as e:
            logger.error(f"Section classification LLM error: {e}")
            return SectionType.GENERAL

    def _parse_section_type(self, content: str) -> SectionType:
        content = re.sub(r"```(?:json)?|```", "", content).strip()
        try:
            data = json.loads(content)
            raw = data.get("section_type", "general").strip().lower()
            try:
                return SectionType(raw)
            except ValueError:
                return SectionType.GENERAL
        except (json.JSONDecodeError, KeyError):
            logger.warning(f"Could not parse section type from: {content}")
            return SectionType.GENERAL
