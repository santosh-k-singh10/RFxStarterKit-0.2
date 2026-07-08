"""
core/schemas.py
---------------
All Pydantic data models for the RFP Analyzer.
Every agent reads and writes these models — they are the contract between stages.
"""

from __future__ import annotations

import operator
from enum import Enum
from typing import Optional, Annotated, TypedDict
from datetime import datetime
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

class Category(str, Enum):
    FUNCTIONAL     = "functional"
    NON_FUNCTIONAL = "non_functional"
    COMPLIANCE     = "compliance"
    AMBIGUITY      = "ambiguity"
    RISK           = "risk"


class Priority(str, Enum):
    MUST   = "must"
    SHOULD = "should"
    COULD  = "could"
    WONT   = "wont"


class ReviewStatus(str, Enum):
    """Review workflow status for requirements."""
    PENDING  = "pending"      # Initial state
    ACCEPTED = "accepted"     # Approved for implementation
    MODIFIED = "modified"     # Edited by reviewer
    REJECTED = "rejected"     # Dropped/ignored


# ─────────────────────────────────────────────────────────────────────────────
# Core requirement model
# ─────────────────────────────────────────────────────────────────────────────

class Requirement(BaseModel):
    """A single extracted requirement from the RFP."""

    id: str = ""
    # e.g. "FR-001", "NFR-012", "CR-003"

    category: Category = Category.FUNCTIONAL

    title: str = ""
    # Short label, max ~10 words

    description: str = ""
    # Clear, implementation-neutral description of what is required

    source_section: str = ""
    # Exact section heading from the RFP where this was found

    page_ref: Optional[str] = None
    # Page number string, e.g. "12" or "12-13"

    priority: Priority = Priority.MUST
    # MoSCoW priority inferred from language ("shall" → must, "should" → should)

    confidence: float = Field(default=0.9, ge=0.0, le=1.0)
    # How clearly stated: 1.0 = explicitly stated, <0.7 = implicit or vague

    ambiguity_flag: bool = False
    # True if this item is vague, contradictory, or needs clarification

    clarification_question: Optional[str] = None
    # If ambiguous, the specific question that needs an answer

    related_ids: list[str] = Field(default_factory=list)
    # IDs of requirements cross-linked during synthesis

    raw_excerpt: str = ""
    # The exact text from the RFP that produced this requirement

    # ── Review workflow fields ──────────────────────────────────────────────
    review_status: ReviewStatus = ReviewStatus.PENDING
    # Workflow status for requirement review process

    reviewer_notes: Optional[str] = None
    # Notes added by reviewer during review process

    clarification_answer: Optional[str] = None
    # Answer provided to clarification question

    answer_source: Optional[str] = None
    # Source of the clarification answer (e.g., "Corrigendum No. 1")

    reanalysis_triggered: bool = False
    # Flag indicating if requirement was re-analyzed after clarification

    # ── Architecture & Solution Mapping ─────────────────────────────────────
    system_components: list[str] = Field(default_factory=list)
    # System components this requirement relates to

    best_fit_solution: Optional[str] = None
    # Best-fit solution for this requirement (e.g., "SAP S/4HANA")

    solution_coverage: Optional[str] = None
    # Coverage type: native | configuration | customisation | gap

    solution_module: Optional[str] = None
    # Specific module/feature in the solution

    solution_rationale: Optional[str] = None
    # Rationale for solution selection


# ─────────────────────────────────────────────────────────────────────────────
# Document chunk model
# ─────────────────────────────────────────────────────────────────────────────

class DocumentChunk(BaseModel):
    """A section-aware chunk of the source RFP document."""

    section: str = "Preamble"
    text: str = ""
    page: int = 1
    char_count: int = 0

    def is_substantial(self, min_chars: int = 100) -> bool:
        return len(self.text.strip()) >= min_chars


# ─────────────────────────────────────────────────────────────────────────────
# LangGraph state — passed between every node
# ─────────────────────────────────────────────────────────────────────────────

class AnalysisStateDict(TypedDict, total=False):
    """
    TypedDict-based state for LangGraph with Annotated reducers for concurrent updates.
    This allows parallel agents to update different fields simultaneously.
    Using total=False makes all fields optional with defaults.
    """
    # Input
    file_path: str
    
    # After ingestion
    document_text: str
    chunks: list[DocumentChunk]
    
    # Per-agent outputs - use operator.add to concatenate lists from parallel agents
    functional: Annotated[list[Requirement], operator.add]
    non_functional: Annotated[list[Requirement], operator.add]
    compliance: Annotated[list[Requirement], operator.add]
    ambiguities: Annotated[list[Requirement], operator.add]
    risks: Annotated[list[Requirement], operator.add]
    
    # Final synthesized output
    final_requirements: list[Requirement]
    
    # Run metadata
    metadata: dict
    errors: Annotated[list[str], operator.add]


class AnalysisState(BaseModel):
    """
    Pydantic version of the state for validation and serialization.
    The shared state object threaded through every LangGraph node.
    Each node reads what it needs and writes back its results.
    """

    # Input
    file_path: str = ""

    # After ingestion
    document_text: str = ""
    chunks: list[DocumentChunk] = Field(default_factory=list)

    # Per-agent outputs
    functional:     list[Requirement] = Field(default_factory=list)
    non_functional: list[Requirement] = Field(default_factory=list)
    compliance:     list[Requirement] = Field(default_factory=list)
    ambiguities:    list[Requirement] = Field(default_factory=list)
    risks:          list[Requirement] = Field(default_factory=list)

    # Final synthesized output
    final_requirements: list[Requirement] = Field(default_factory=list)

    # Run metadata
    metadata: dict = Field(default_factory=dict)
    errors:   list[str] = Field(default_factory=list)

    def all_raw_requirements(self) -> list[Requirement]:
        return (
            self.functional +
            self.non_functional +
            self.compliance +
            self.ambiguities +
            self.risks
        )


# ─────────────────────────────────────────────────────────────────────────────
# Session context model for web application
# ─────────────────────────────────────────────────────────────────────────────

class RFPContext(BaseModel):
    """Session context for an RFP analysis in the web application."""
    
    session_id: str
    file_path: str
    title: str
    domain: Optional[str] = None
    state: AnalysisState
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Cached Claude API results
    architecture_diagram: Optional[str] = None
    system_components: list[dict] = Field(default_factory=list)
    solution_map: Optional[dict] = None
