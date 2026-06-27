"""
phase0/schema.py
All Pydantic models for Phase 0 Document Router Agent.
These are the shared contracts between sub-agents and downstream phases.
"""

from __future__ import annotations
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class DocType(str, Enum):
    TECHNICAL_SPEC       = "technical_spec"
    COMPLIANCE           = "compliance"
    PRICING_TEMPLATE     = "pricing_template"
    COVER_LETTER         = "cover_letter"
    REFERENCE_ARCH       = "reference_architecture"
    SOW                  = "statement_of_work"
    TERMS_AND_CONDITIONS = "terms_and_conditions"
    UNKNOWN              = "unknown"


class SectionType(str, Enum):
    FUNCTIONAL_REQUIREMENT     = "functional_requirement"
    NON_FUNCTIONAL_REQUIREMENT = "non_functional_requirement"
    TIMELINE                   = "timeline"
    PRICING                    = "pricing"
    COMPLIANCE_CLAUSE          = "compliance_clause"
    ARCHITECTURE_NOTE          = "architecture_note"
    SCOPE                      = "scope"
    ASSUMPTION                 = "assumption"
    GLOSSARY                   = "glossary"
    GENERAL                    = "general"


class PhaseTarget(str, Enum):
    PHASE1 = "phase1"
    PHASE2 = "phase2"
    PHASE3 = "phase3"
    ALL    = "all"


# ---------------------------------------------------------------------------
# Classifier output
# ---------------------------------------------------------------------------

class ClassifiedDocument(BaseModel):
    filename: str
    doc_type: DocType
    confidence: float = Field(ge=0.0, le=1.0)
    raw_text: str                        # full extracted text
    pages: int = 0
    needs_review: bool = False           # True when confidence < threshold


# ---------------------------------------------------------------------------
# Chunk (core unit that flows through the entire pipeline)
# ---------------------------------------------------------------------------

class Chunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"ch_{uuid.uuid4().hex[:8]}")
    source_document: str                 # originating filename
    page_ref: str                        # e.g. "p.4-5"
    doc_type: DocType
    section_type: SectionType
    phase_relevance: List[PhaseTarget]
    conflict_flag: bool = False
    conflict_ref: Optional[str] = None  # conflict_id if flagged
    content: str


# ---------------------------------------------------------------------------
# Conflict
# ---------------------------------------------------------------------------

class Conflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: f"C{uuid.uuid4().hex[:4].upper()}")
    chunk_ids: List[str]                 # the two (or more) conflicting chunk ids
    source_documents: List[str]          # filenames involved
    description: str                     # human-readable summary of the conflict
    severity: str = "medium"            # low / medium / high


# ---------------------------------------------------------------------------
# Context assembler output (per-phase slice)
# ---------------------------------------------------------------------------

class PhaseContext(BaseModel):
    phase: PhaseTarget
    chunks: List[Chunk]
    total_tokens_estimate: int = 0


# ---------------------------------------------------------------------------
# Final document_context (output of Phase 0 — input to all downstream phases)
# ---------------------------------------------------------------------------

class DocumentContext(BaseModel):
    rfp_id: str = Field(default_factory=lambda: f"RFP-{uuid.uuid4().hex[:8].upper()}")
    documents: List[ClassifiedDocument]
    phase_contexts: Dict[str, PhaseContext]  # keyed by PhaseTarget value
    conflicts: List[Conflict] = []
    metadata: Dict[str, Any] = {}

    def get_phase_chunks(self, phase: PhaseTarget) -> List[Chunk]:
        """Convenience accessor for downstream phases."""
        ctx = self.phase_contexts.get(phase.value)
        return ctx.chunks if ctx else []

    def has_conflicts(self) -> bool:
        return len(self.conflicts) > 0


# ---------------------------------------------------------------------------
# API request / response wrappers
# ---------------------------------------------------------------------------

class Phase0Response(BaseModel):
    success: bool
    rfp_id: str
    document_context: DocumentContext
    warnings: List[str] = []
    errors: List[str] = []
