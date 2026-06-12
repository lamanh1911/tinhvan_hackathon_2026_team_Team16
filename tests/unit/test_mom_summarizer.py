"""Unit tests — MOMSummarizerService (FR-05).

Tests cover _build_mom, _normalize_action, and incomplete_warning logic.
No external calls, no database.
"""
from datetime import date

import pytest

from src.api.services.mom_summarizer import (
    MOMSummarizerService,
    _build_mom,
    _normalize_action,
    _parse_deadline,
)
from src.api.services.llm_client import MockLLMClient


# ---------------------------------------------------------------------------
# _parse_deadline
# ---------------------------------------------------------------------------

class TestParseDeadline:
    def test_parses_iso_string(self):
        assert _parse_deadline("2026-07-01") == date(2026, 7, 1)

    def test_returns_date_object_unchanged(self):
        d = date(2026, 6, 15)
        assert _parse_deadline(d) == d

    def test_returns_none_for_empty_string(self):
        assert _parse_deadline("") is None

    def test_returns_none_for_none(self):
        assert _parse_deadline(None) is None

    def test_returns_none_for_invalid_format(self):
        assert _parse_deadline("next week") is None


# ---------------------------------------------------------------------------
# _normalize_action
# ---------------------------------------------------------------------------

class TestNormalizeAction:
    def test_returns_none_for_empty_description(self):
        assert _normalize_action({"description": "", "owner": "Alice"}) is None

    def test_returns_none_for_missing_description(self):
        assert _normalize_action({"owner": "Alice"}) is None

    def test_owner_stripped(self):
        result = _normalize_action({"description": "Task", "owner": "  Bob  "})
        assert result["owner"] == "Bob"

    def test_owner_none_when_blank(self):
        result = _normalize_action({"description": "Task", "owner": "  "})
        assert result["owner"] is None

    def test_deadline_parsed(self):
        result = _normalize_action({"description": "Task", "owner": "Bob", "deadline": "2026-07-01"})
        assert result["deadline"] == date(2026, 7, 1)


# ---------------------------------------------------------------------------
# _build_mom
# ---------------------------------------------------------------------------

class TestBuildMom:
    def _full_raw(self):
        return {
            "summary": "Discussed Q3 roadmap and next steps.",
            "language": "en",
            "incomplete_warning": False,
            "next_actions": [
                {"description": "Prepare slides", "owner": "Alice", "deadline": "2026-07-01"},
                {"description": "Book venue", "owner": "Bob", "deadline": "2026-07-05"},
            ],
        }

    def test_four_required_fields_present(self):
        mom = _build_mom(self._full_raw())
        assert "summary" in mom
        assert "language" in mom
        assert "incomplete_warning" in mom
        assert "action_items" in mom

    def test_summary_populated(self):
        mom = _build_mom(self._full_raw())
        assert mom["summary"] == "Discussed Q3 roadmap and next steps."

    def test_action_items_parsed(self):
        mom = _build_mom(self._full_raw())
        assert len(mom["action_items"]) == 2

    def test_action_item_has_owner_and_deadline(self):
        mom = _build_mom(self._full_raw())
        item = mom["action_items"][0]
        assert item["owner"] == "Alice"
        assert item["deadline"] == date(2026, 7, 1)

    def test_incomplete_when_no_summary(self):
        raw = self._full_raw()
        raw["summary"] = None
        mom = _build_mom(raw)
        assert mom["incomplete_warning"] is True

    def test_incomplete_when_no_action_items(self):
        raw = self._full_raw()
        raw["next_actions"] = []
        mom = _build_mom(raw)
        assert mom["incomplete_warning"] is True

    def test_incomplete_when_action_missing_owner(self):
        raw = self._full_raw()
        raw["next_actions"][0]["owner"] = None
        mom = _build_mom(raw)
        assert mom["incomplete_warning"] is True

    def test_incomplete_when_action_missing_deadline(self):
        raw = self._full_raw()
        raw["next_actions"][0]["deadline"] = None
        mom = _build_mom(raw)
        assert mom["incomplete_warning"] is True

    def test_llm_flag_forces_incomplete(self):
        raw = self._full_raw()
        raw["incomplete_warning"] = True
        mom = _build_mom(raw)
        assert mom["incomplete_warning"] is True


# ---------------------------------------------------------------------------
# MOMSummarizerService with MockLLMClient
# ---------------------------------------------------------------------------

import asyncio


class TestMOMSummarizerService:
    def run(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    def test_summarize_returns_expected_keys(self):
        service = MOMSummarizerService(MockLLMClient())
        result = self.run(service.summarize("Transcript content here."))
        assert "summary" in result
        assert "action_items" in result
        assert "incomplete_warning" in result

    def test_summarize_does_not_return_raw_transcript(self):
        service = MOMSummarizerService(MockLLMClient())
        result = self.run(service.summarize("Confidential transcript."))
        result_str = str(result)
        assert "Confidential transcript" not in result_str
