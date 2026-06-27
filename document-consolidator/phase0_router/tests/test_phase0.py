"""
tests/test_phase0.py
Unit tests for Phase 0 sub-agents using mocked LLM responses.
Run with: pytest tests/ -v
"""

from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile
import pytest

from phase0.schema import (
    DocType, SectionType, PhaseTarget,
    ClassifiedDocument, Chunk, Conflict,
)
from phase0.classifier import ClassifierAgent
from phase0.chunker import ChunkerAgent, PHASE_ROUTING
from phase0.conflict_detector import ConflictDetectorAgent
from phase0.assembler import ContextAssembler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_client(response_text: str):
    """Returns a mock Anthropic client that returns response_text."""
    mock_content = MagicMock()
    mock_content.text = response_text
    mock_response = MagicMock()
    mock_response.content = [mock_content]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response
    return mock_client


def make_chunk(
    content="Sample requirement text.",
    source="doc_a.pdf",
    section_type=SectionType.FUNCTIONAL_REQUIREMENT,
    doc_type=DocType.TECHNICAL_SPEC,
    phase_relevance=None,
) -> Chunk:
    return Chunk(
        source_document=source,
        page_ref="p.1",
        doc_type=doc_type,
        section_type=section_type,
        phase_relevance=phase_relevance or [PhaseTarget.PHASE1, PhaseTarget.PHASE2],
        content=content,
    )


def make_classified_doc(filename="test.pdf", doc_type=DocType.TECHNICAL_SPEC) -> ClassifiedDocument:
    return ClassifiedDocument(
        filename=filename,
        doc_type=doc_type,
        confidence=0.92,
        raw_text="System shall support 10,000 concurrent users. Availability must be 99.9%.",
        pages=5,
    )


# ---------------------------------------------------------------------------
# Classifier tests
# ---------------------------------------------------------------------------

class TestClassifierAgent:

    def test_classifies_technical_spec(self):
        mock_response = json.dumps({
            "doc_type": "technical_spec",
            "confidence": 0.95,
            "reasoning": "Contains functional and non-functional requirements.",
        })
        agent = ClassifierAgent(client=make_mock_client(mock_response))

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("The system shall process 1000 transactions per second.")
            tmp_path = f.name

        result = agent.classify(tmp_path)
        assert result.doc_type == DocType.TECHNICAL_SPEC
        assert result.confidence == 0.95
        assert result.needs_review is False

    def test_flags_low_confidence_for_review(self):
        mock_response = json.dumps({
            "doc_type": "unknown",
            "confidence": 0.40,
            "reasoning": "Cannot determine document type.",
        })
        agent = ClassifierAgent(client=make_mock_client(mock_response))

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("Some ambiguous content here.")
            tmp_path = f.name

        result = agent.classify(tmp_path)
        assert result.needs_review is True
        assert result.doc_type == DocType.UNKNOWN

    def test_handles_empty_file(self):
        agent = ClassifierAgent(client=make_mock_client("{}"))

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("")
            tmp_path = f.name

        result = agent.classify(tmp_path)
        assert result.doc_type == DocType.UNKNOWN
        assert result.needs_review is True

    def test_handles_malformed_llm_response(self):
        agent = ClassifierAgent(client=make_mock_client("not json at all"))

        with tempfile.NamedTemporaryFile(suffix=".txt", mode="w", delete=False) as f:
            f.write("Some content.")
            tmp_path = f.name

        result = agent.classify(tmp_path)
        assert result.doc_type == DocType.UNKNOWN


# ---------------------------------------------------------------------------
# Chunker tests
# ---------------------------------------------------------------------------

class TestChunkerAgent:

    def test_chunks_document_into_sections(self):
        mock_response = json.dumps({
            "section_type": "functional_requirement",
            "confidence": 0.88,
        })
        agent = ChunkerAgent(client=make_mock_client(mock_response))
        doc = make_classified_doc()
        # Give it enough content to produce at least one chunk
        doc.raw_text = "Requirement A. " * 100

        chunks = agent.chunk(doc)
        assert len(chunks) >= 1
        assert all(isinstance(c, Chunk) for c in chunks)
        assert all(c.source_document == "test.pdf" for c in chunks)

    def test_phase_routing_functional_req(self):
        relevance = PHASE_ROUTING[SectionType.FUNCTIONAL_REQUIREMENT]
        assert PhaseTarget.PHASE1 in relevance
        assert PhaseTarget.PHASE2 in relevance

    def test_phase_routing_pricing_goes_to_phase3(self):
        relevance = PHASE_ROUTING[SectionType.PRICING]
        assert PhaseTarget.PHASE3 in relevance
        assert PhaseTarget.PHASE1 not in relevance

    def test_chunk_ids_are_unique(self):
        mock_response = json.dumps({"section_type": "general", "confidence": 0.5})
        agent = ChunkerAgent(client=make_mock_client(mock_response))
        doc = make_classified_doc()
        doc.raw_text = "Content block. " * 200

        chunks = agent.chunk(doc)
        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids)), "Chunk IDs must be unique"


# ---------------------------------------------------------------------------
# Conflict Detector tests
# ---------------------------------------------------------------------------

class TestConflictDetectorAgent:

    def test_detects_conflict_between_docs(self):
        mock_response = json.dumps({
            "is_conflict": True,
            "severity": "high",
            "description": "Doc A specifies 99.9% SLA; Doc B specifies 99.5% SLA.",
        })
        agent = ConflictDetectorAgent(client=make_mock_client(mock_response))

        chunk_a = make_chunk(
            content="System availability shall be 99.9% uptime.",
            source="tech_spec.pdf",
            section_type=SectionType.NON_FUNCTIONAL_REQUIREMENT,
        )
        chunk_b = make_chunk(
            content="Availability requirement: 99.5% uptime per month.",
            source="compliance.pdf",
            section_type=SectionType.NON_FUNCTIONAL_REQUIREMENT,
        )

        conflicts = agent.detect([chunk_a, chunk_b])
        assert len(conflicts) == 1
        assert conflicts[0].severity == "high"
        assert chunk_a.conflict_flag is True
        assert chunk_b.conflict_flag is True
        assert chunk_a.conflict_ref == conflicts[0].conflict_id

    def test_no_conflict_same_document(self):
        """Chunks from the same document should never be compared."""
        mock_response = json.dumps({
            "is_conflict": True,
            "severity": "high",
            "description": "Conflict found.",
        })
        agent = ConflictDetectorAgent(client=make_mock_client(mock_response))

        chunk_a = make_chunk(source="same_doc.pdf", section_type=SectionType.SCOPE)
        chunk_b = make_chunk(source="same_doc.pdf", section_type=SectionType.SCOPE)

        conflicts = agent.detect([chunk_a, chunk_b])
        # LLM should never have been called — same source doc
        assert len(conflicts) == 0

    def test_no_conflict_returns_empty(self):
        mock_response = json.dumps({
            "is_conflict": False,
            "severity": "low",
            "description": "",
        })
        agent = ConflictDetectorAgent(client=make_mock_client(mock_response))

        chunk_a = make_chunk(source="doc_a.pdf", section_type=SectionType.COMPLIANCE_CLAUSE)
        chunk_b = make_chunk(source="doc_b.pdf", section_type=SectionType.COMPLIANCE_CLAUSE)

        conflicts = agent.detect([chunk_a, chunk_b])
        assert len(conflicts) == 0
        assert chunk_a.conflict_flag is False


# ---------------------------------------------------------------------------
# Context Assembler tests
# ---------------------------------------------------------------------------

class TestContextAssembler:

    def test_assembles_document_context(self):
        assembler = ContextAssembler()
        docs = [make_classified_doc("doc_a.pdf"), make_classified_doc("doc_b.pdf")]
        chunks = [
            make_chunk(phase_relevance=[PhaseTarget.PHASE1, PhaseTarget.PHASE2]),
            make_chunk(phase_relevance=[PhaseTarget.PHASE3]),
            make_chunk(phase_relevance=[PhaseTarget.ALL]),
        ]
        result = assembler.assemble(docs, chunks, [])

        assert result.metadata["total_docs"] == 2
        assert result.metadata["total_chunks"] == 3
        assert "phase1" in result.phase_contexts
        assert "phase3" in result.phase_contexts

    def test_all_chunks_appear_in_every_phase(self):
        assembler = ContextAssembler()
        docs = [make_classified_doc()]
        all_chunk = make_chunk(phase_relevance=[PhaseTarget.ALL])
        result = assembler.assemble(docs, [all_chunk], [])

        for phase in ["phase1", "phase2", "phase3"]:
            assert any(
                c.chunk_id == all_chunk.chunk_id
                for c in result.phase_contexts[phase].chunks
            ), f"ALL chunk missing from {phase}"

    def test_deduplication_removes_duplicates(self):
        assembler = ContextAssembler()
        docs = [make_classified_doc()]
        # Same content, same phase → should deduplicate
        chunk1 = make_chunk(content="Identical content block.", phase_relevance=[PhaseTarget.PHASE1])
        chunk2 = make_chunk(content="Identical content block.", phase_relevance=[PhaseTarget.PHASE1])

        result = assembler.assemble(docs, [chunk1, chunk2], [])
        phase1_chunks = result.phase_contexts["phase1"].chunks
        assert len(phase1_chunks) == 1

    def test_conflict_count_in_metadata(self):
        assembler = ContextAssembler()
        docs = [make_classified_doc()]
        conflict = Conflict(
            chunk_ids=["ch_001", "ch_002"],
            source_documents=["a.pdf", "b.pdf"],
            description="SLA mismatch",
        )
        result = assembler.assemble(docs, [], [conflict])
        assert result.metadata["conflict_count"] == 1
        assert result.has_conflicts() is True
