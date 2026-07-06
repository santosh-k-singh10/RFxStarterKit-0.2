"""
tests/unit/test_synthesizer.py
-------------------------------
Unit tests for agents/synthesizer.py.

All tests are pure Python — no LLM calls, no network.
_cross_link is patched out wherever it would call the API.
"""

import pytest

from agents.synthesizer import _normalise_title, _deduplicate, synthesize, _PRIORITY_ORDER, _CATEGORY_ORDER
from core.schemas import Category, Priority, Requirement


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _req(
    req_id: str,
    title: str,
    category: Category = Category.FUNCTIONAL,
    priority: Priority = Priority.MUST,
    confidence: float = 0.9,
) -> Requirement:
    return Requirement(
        id=req_id,
        title=title,
        category=category,
        priority=priority,
        confidence=confidence,
    )


# ─────────────────────────────────────────────────────────────────────────────
# _normalise_title
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestNormaliseTitle:
    def test_lowercases(self):
        assert _normalise_title("User Authentication") == "user authentication"

    def test_strips_hyphens(self):
        assert _normalise_title("Aadhaar-based login") == "aadhaar based login"

    def test_strips_underscores(self):
        assert _normalise_title("data_export") == "data export"

    def test_collapses_whitespace(self):
        assert _normalise_title("user  login   flow") == "user login flow"

    def test_strips_punctuation(self):
        # The regex keeps parentheses; only non-word, non-space, non-paren chars are stripped.
        # "Login (OAuth 2.0)!" → "login (oauth 20)"
        assert _normalise_title("Login (OAuth 2.0)!") == "login (oauth 20)"

    def test_empty_string(self):
        assert _normalise_title("") == ""

    def test_already_normalised(self):
        assert _normalise_title("user login") == "user login"


# ─────────────────────────────────────────────────────────────────────────────
# _deduplicate
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestDeduplicate:
    def test_no_duplicates_unchanged(self):
        reqs = [
            _req("FR-001", "User Login"),
            _req("FR-002", "Document Upload"),
        ]
        result = _deduplicate(reqs)
        assert len(result) == 2

    def test_exact_title_duplicate_removed(self):
        reqs = [
            _req("FR-001", "User Login", confidence=0.8),
            _req("FR-002", "User Login", confidence=0.9),
        ]
        result = _deduplicate(reqs)
        assert len(result) == 1
        # Keeps the higher-confidence one
        assert result[0].confidence == 0.9

    def test_case_insensitive_dedup(self):
        reqs = [
            _req("FR-001", "user login", confidence=0.7),
            _req("FR-002", "User Login", confidence=0.85),
        ]
        result = _deduplicate(reqs)
        assert len(result) == 1
        assert result[0].confidence == 0.85

    def test_same_title_different_category_kept(self):
        """Same title in different categories are NOT duplicates."""
        reqs = [
            _req("FR-001", "User Login", category=Category.FUNCTIONAL),
            _req("NFR-001", "User Login", category=Category.NON_FUNCTIONAL),
        ]
        result = _deduplicate(reqs)
        assert len(result) == 2

    def test_empty_input(self):
        assert _deduplicate([]) == []

    def test_single_item_unchanged(self):
        reqs = [_req("FR-001", "User Login")]
        result = _deduplicate(reqs)
        assert len(result) == 1


# ─────────────────────────────────────────────────────────────────────────────
# synthesize — sort order (patch _cross_link to avoid LLM call)
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestSynthesizeSortOrder:
    def test_categories_sorted_correctly(self, monkeypatch):
        """Functional < NonFunctional < Compliance < Ambiguity < Risk."""
        monkeypatch.setattr("agents.synthesizer._cross_link", lambda reqs: reqs)

        reqs = [
            _req("RISK-001", "Delivery risk",     category=Category.RISK),
            _req("FR-001",   "User login",         category=Category.FUNCTIONAL),
            _req("CR-001",   "GDPR compliance",    category=Category.COMPLIANCE),
            _req("NFR-001",  "Performance target", category=Category.NON_FUNCTIONAL),
            _req("AMB-001",  "Ambiguous SLA",      category=Category.AMBIGUITY),
        ]
        result = synthesize(reqs)

        categories = [r.category for r in result]
        assert categories == [
            Category.FUNCTIONAL,
            Category.NON_FUNCTIONAL,
            Category.COMPLIANCE,
            Category.AMBIGUITY,
            Category.RISK,
        ]

    def test_priorities_sorted_within_category(self, monkeypatch):
        """Within one category: MUST < SHOULD < COULD < WONT."""
        monkeypatch.setattr("agents.synthesizer._cross_link", lambda reqs: reqs)

        reqs = [
            _req("FR-003", "Nice-to-have export", priority=Priority.COULD),
            _req("FR-001", "Core login",           priority=Priority.MUST),
            _req("FR-002", "Dashboard filter",     priority=Priority.SHOULD),
        ]
        result = synthesize(reqs)
        priorities = [r.priority for r in result]
        assert priorities == [Priority.MUST, Priority.SHOULD, Priority.COULD]

    def test_empty_list_returns_empty(self, monkeypatch):
        monkeypatch.setattr("agents.synthesizer._cross_link", lambda reqs: reqs)
        assert synthesize([]) == []

    def test_dedup_runs_before_sort(self, monkeypatch):
        """Duplicate with lower confidence is dropped even when it appears first."""
        monkeypatch.setattr("agents.synthesizer._cross_link", lambda reqs: reqs)

        reqs = [
            _req("FR-001", "User Login", confidence=0.6),
            _req("FR-002", "User Login", confidence=0.95),
            _req("FR-003", "Data Export"),
        ]
        result = synthesize(reqs)
        assert len(result) == 2
        login = next(r for r in result if "login" in r.title.lower())
        assert login.confidence == 0.95
