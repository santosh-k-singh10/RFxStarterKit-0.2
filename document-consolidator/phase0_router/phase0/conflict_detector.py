"""
phase0/conflict_detector.py
Conflict Detector Agent — identifies contradictions across chunks from different documents.

Strategy:
- Groups chunks by section_type
- For types likely to conflict (NFRs, timelines, pricing, scope), compares chunks
  from different source documents pairwise
- Uses LLM to assess whether two chunks genuinely conflict
- Returns list of Conflict objects with severity rating

Performance note:
- Only compares chunks from DIFFERENT source documents (same-doc chunks rarely conflict)
- Limits pairwise comparisons using a configurable cap to avoid O(n²) LLM calls
- High-value section types are checked first; GENERAL/GLOSSARY are skipped
"""

from __future__ import annotations
import json
import logging
import re
from itertools import combinations
from typing import List

from .schema import Chunk, Conflict, SectionType

logger = logging.getLogger(__name__)

# Only check these section types for conflicts — others rarely produce meaningful conflicts
CONFLICT_SECTION_TYPES = {
    SectionType.NON_FUNCTIONAL_REQUIREMENT,
    SectionType.TIMELINE,
    SectionType.PRICING,
    SectionType.SCOPE,
    SectionType.COMPLIANCE_CLAUSE,
    SectionType.ASSUMPTION,
}

# Max pairs to check per section type (avoids combinatorial explosion on large packs)
MAX_PAIRS_PER_SECTION = 20


CONFLICT_CHECK_PROMPT = """You are reviewing two text chunks from different documents in an RFP pack.
Determine if they contradict each other on a specific, material point (e.g. different SLA numbers,
conflicting scope boundaries, different timelines, inconsistent pricing terms).

Minor wording differences or complementary information are NOT conflicts.

Respond ONLY with JSON (no markdown):
{{
  "is_conflict": <true or false>,
  "severity": "<low|medium|high>",
  "description": "<one sentence describing the specific contradiction, or empty string if no conflict>"
}}

Chunk A (from: {doc_a}):
---
{text_a}
---

Chunk B (from: {doc_b}):
---
{text_b}
---"""


class ConflictDetectorAgent:
    """
    Detects cross-document conflicts in a list of chunks.
    Mutates chunk.conflict_flag and chunk.conflict_ref in place.
    Returns a list of Conflict objects.
    """

    def __init__(self, client = None):
        """
        Initialize ConflictDetectorAgent with an LLM client.
        
        Args:
            client: Anthropic client or OpenAI-compatible wrapper. If None, uses get_anthropic_client().
        """
        if client is None:
            from .llm_client import get_anthropic_client
            client = get_anthropic_client()
        self.client = client

    def detect(self, all_chunks: List[Chunk]) -> List[Conflict]:
        """
        Main entry point.

        Args:
            all_chunks: all chunks from all documents (output of ChunkerAgent)

        Returns:
            List of Conflict objects. Also mutates conflict_flag/conflict_ref on affected chunks.
        """
        conflicts: List[Conflict] = []

        # Group chunks by section type, filtering to conflict-prone types
        by_section: dict[SectionType, List[Chunk]] = {}
        for chunk in all_chunks:
            if chunk.section_type in CONFLICT_SECTION_TYPES:
                by_section.setdefault(chunk.section_type, []).append(chunk)

        for section_type, chunks in by_section.items():
            # Only compare chunks from DIFFERENT documents
            cross_doc_pairs = [
                (a, b) for a, b in combinations(chunks, 2)
                if a.source_document != b.source_document
            ]

            if not cross_doc_pairs:
                continue

            # Cap pairs to avoid excessive LLM calls
            pairs_to_check = cross_doc_pairs[:MAX_PAIRS_PER_SECTION]
            logger.info(
                f"Conflict check: {section_type.value} — "
                f"{len(pairs_to_check)} pairs across documents"
            )

            for chunk_a, chunk_b in pairs_to_check:
                conflict = self._check_pair(chunk_a, chunk_b)
                if conflict:
                    conflicts.append(conflict)
                    # Mutate chunks so downstream phases can see the flag
                    chunk_a.conflict_flag = True
                    chunk_a.conflict_ref = conflict.conflict_id
                    chunk_b.conflict_flag = True
                    chunk_b.conflict_ref = conflict.conflict_id

        logger.info(f"Conflict detection complete: {len(conflicts)} conflicts found")
        return conflicts

    def _check_pair(self, chunk_a: Chunk, chunk_b: Chunk) -> Conflict | None:
        """
        Asks LLM whether two chunks conflict.
        Returns a Conflict object if yes, None otherwise.
        """
        prompt = CONFLICT_CHECK_PROMPT.format(
            doc_a=chunk_a.source_document,
            text_a=chunk_a.content[:800],
            doc_b=chunk_b.source_document,
            text_b=chunk_b.content[:800],
        )

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}],
            )
            # Support both anthropic.types.TextBlock and our ContentBlock wrapper
            first_block = response.content[0]
            if hasattr(first_block, "text"):
                content = first_block.text.strip()
            else:
                logger.error(f"Unexpected content block type: {type(first_block)}")
                return None
            return self._parse_conflict(content, chunk_a, chunk_b)

        except Exception as e:
            logger.error(f"Conflict LLM call failed: {e}")
            return None

    def _parse_conflict(
        self, content: str, chunk_a: Chunk, chunk_b: Chunk
    ) -> Conflict | None:
        content = re.sub(r"```(?:json)?|```", "", content).strip()
        try:
            data = json.loads(content)
            if not data.get("is_conflict", False):
                return None

            return Conflict(
                chunk_ids=[chunk_a.chunk_id, chunk_b.chunk_id],
                source_documents=[chunk_a.source_document, chunk_b.source_document],
                description=data.get("description", "Unspecified conflict"),
                severity=data.get("severity", "medium"),
            )

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse conflict response: {e}\nRaw: {content}")
            return None
