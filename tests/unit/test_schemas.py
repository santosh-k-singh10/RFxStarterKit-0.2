"""
tests/unit/test_schemas.py
--------------------------
Unit tests for core/schemas.py — Requirement, DocumentChunk, enums.

Pure Python, no network, no LLM.
"""

import pytest
from pydantic import ValidationError

from core.schemas import (
    Category,
    Priority,
    ReviewStatus,
    Requirement,
    DocumentChunk,
)


# ─────────────────────────────────────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestEnums:
    def test_category_values(self):
        assert Category.FUNCTIONAL.value == "functional"
        assert Category.NON_FUNCTIONAL.value == "non_functional"
        assert Category.COMPLIANCE.value == "compliance"
        assert Category.AMBIGUITY.value == "ambiguity"
        assert Category.RISK.value == "risk"

    def test_priority_values(self):
        assert Priority.MUST.value == "must"
        assert Priority.SHOULD.value == "should"
        assert Priority.COULD.value == "could"
        assert Priority.WONT.value == "wont"

    def test_review_status_values(self):
        assert ReviewStatus.PENDING.value == "pending"
        assert ReviewStatus.ACCEPTED.value == "accepted"
        assert ReviewStatus.MODIFIED.value == "modified"
        assert ReviewStatus.REJECTED.value == "rejected"

    def test_category_from_string(self):
        assert Category("functional") == Category.FUNCTIONAL
        assert Category("risk") == Category.RISK

    def test_priority_from_string(self):
        assert Priority("must") == Priority.MUST
        assert Priority("wont") == Priority.WONT


# ─────────────────────────────────────────────────────────────────────────────
# Requirement model
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestRequirement:
    def test_defaults(self):
        req = Requirement()
        assert req.id == ""
        assert req.category == Category.FUNCTIONAL
        assert req.priority == Priority.MUST
        assert req.confidence == 0.9
        assert req.ambiguity_flag is False
        assert req.related_ids == []
        assert req.review_status == ReviewStatus.PENDING

    def test_construct_with_values(self):
        req = Requirement(
            id="FR-001",
            title="User authentication",
            category=Category.FUNCTIONAL,
            priority=Priority.MUST,
            confidence=0.95,
            ambiguity_flag=False,
        )
        assert req.id == "FR-001"
        assert req.title == "User authentication"
        assert req.confidence == 0.95

    def test_confidence_lower_bound(self):
        with pytest.raises(ValidationError):
            Requirement(confidence=-0.1)

    def test_confidence_upper_bound(self):
        with pytest.raises(ValidationError):
            Requirement(confidence=1.1)

    def test_confidence_boundary_values(self):
        assert Requirement(confidence=0.0).confidence == 0.0
        assert Requirement(confidence=1.0).confidence == 1.0

    def test_related_ids_default_empty(self):
        req = Requirement()
        assert isinstance(req.related_ids, list)
        assert len(req.related_ids) == 0

    def test_sap_modules_default_empty(self):
        req = Requirement()
        assert req.sap_modules == []

    def test_category_string_coercion(self):
        req = Requirement(category="compliance")
        assert req.category == Category.COMPLIANCE

    def test_priority_string_coercion(self):
        req = Requirement(priority="should")
        assert req.priority == Priority.SHOULD


# ─────────────────────────────────────────────────────────────────────────────
# DocumentChunk model
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestDocumentChunk:
    def test_defaults(self):
        chunk = DocumentChunk()
        assert chunk.section == "Preamble"
        assert chunk.text == ""
        assert chunk.page == 1
        assert chunk.char_count == 0

    def test_is_substantial_false_for_short_text(self):
        chunk = DocumentChunk(text="Short")
        assert chunk.is_substantial() is False

    def test_is_substantial_true_for_long_text(self):
        chunk = DocumentChunk(text="A" * 101)
        assert chunk.is_substantial() is True

    def test_is_substantial_exact_boundary(self):
        chunk = DocumentChunk(text="A" * 100)
        assert chunk.is_substantial(min_chars=100) is True

    def test_is_substantial_custom_threshold(self):
        chunk = DocumentChunk(text="A" * 50)
        assert chunk.is_substantial(min_chars=50) is True
        assert chunk.is_substantial(min_chars=51) is False
