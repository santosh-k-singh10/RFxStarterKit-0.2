"""
tests/unit/test_agents_base.py
-------------------------------
Unit tests for agents/base.py — JSON parsing and fence-stripping.

Pure Python, no network.  The OpenAI client is never instantiated
because we only test _parse_json_response directly.
"""

import pytest

from agents.base import _parse_json_response


# ─────────────────────────────────────────────────────────────────────────────
# _parse_json_response
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.unit
class TestParseJsonResponse:
    # --- plain JSON ---

    def test_plain_array(self):
        raw = '[{"id": "FR-001", "title": "Login"}]'
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001", "title": "Login"}]

    def test_plain_empty_array(self):
        assert _parse_json_response("[]") == []

    def test_plain_object_wrapped_in_list(self):
        """A bare dict response is wrapped in a list for consistency."""
        raw = '{"id": "FR-001", "title": "Login"}'
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001", "title": "Login"}]

    def test_multiple_items(self):
        raw = '[{"id": "FR-001"}, {"id": "FR-002"}]'
        result = _parse_json_response(raw)
        assert len(result) == 2
        assert result[0]["id"] == "FR-001"
        assert result[1]["id"] == "FR-002"

    # --- markdown fence stripping ---

    def test_strips_json_fence(self):
        raw = '```json\n[{"id": "FR-001"}]\n```'
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001"}]

    def test_strips_plain_fence(self):
        raw = '```\n[{"id": "FR-001"}]\n```'
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001"}]

    def test_strips_fence_with_trailing_whitespace(self):
        raw = '```json\n[{"id": "FR-001"}]\n```  '
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001"}]

    # --- trailing text after valid JSON ---

    def test_ignores_trailing_text_after_array(self):
        """raw_decode should tolerate markdown explanation after the JSON array."""
        raw = '[{"id": "FR-001"}]\n\nHere is an explanation of the above.'
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001"}]

    def test_ignores_trailing_fence_after_array(self):
        raw = '[{"id": "FR-001"}]\n```'
        result = _parse_json_response(raw)
        assert result == [{"id": "FR-001"}]

    # --- malformed / unrecoverable ---
    # _parse_json_response raises JSONDecodeError for invalid input.
    # The caller (call_claude's retry loop) catches those exceptions.

    def test_raises_on_invalid_json(self):
        import json
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("not json at all")

    def test_raises_on_empty_string(self):
        import json
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response("")

    def test_raises_on_truncated_json(self):
        import json
        with pytest.raises(json.JSONDecodeError):
            _parse_json_response('[{"id": "FR-001"')

    # --- non-list, non-dict parsed values ---

    def test_bare_string_returns_empty(self):
        assert _parse_json_response('"just a string"') == []

    def test_bare_number_returns_empty(self):
        assert _parse_json_response("42") == []

    def test_bare_null_returns_empty(self):
        assert _parse_json_response("null") == []

    # --- nested structures ---

    def test_nested_array_preserved(self):
        raw = '[{"id": "FR-001", "tags": ["auth", "security"]}]'
        result = _parse_json_response(raw)
        assert result[0]["tags"] == ["auth", "security"]

    def test_unicode_content_preserved(self):
        raw = '[{"title": "Aadhaar \u0906\u0927\u093e\u0930"}]'
        result = _parse_json_response(raw)
        assert "Aadhaar" in result[0]["title"]
