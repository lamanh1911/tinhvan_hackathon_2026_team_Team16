"""Integration tests — GraphClientProtocol (FR-03).

Uses MockGraphClient exclusively — no real Microsoft Graph calls.
Verifies the protocol contract that the schedule router depends on.
"""
import asyncio
from datetime import datetime, timezone

import pytest

from src.api.services.graph_client import MockGraphClient


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


EMAILS = ["alice@relay.app", "bob@relay.app"]
START = datetime(2026, 6, 16, 8, 0, tzinfo=timezone.utc)
END = datetime(2026, 6, 16, 18, 0, tzinfo=timezone.utc)


class TestMockGraphClientFreeBusy:
    def test_returns_dict_keyed_by_email(self):
        client = MockGraphClient()
        result = run(client.get_free_busy(EMAILS, START, END))
        assert set(result.keys()) == set(EMAILS)

    def test_mock_returns_empty_busy_blocks(self):
        client = MockGraphClient()
        result = run(client.get_free_busy(EMAILS, START, END))
        for email in EMAILS:
            assert isinstance(result[email], list)
            assert len(result[email]) == 0

    def test_all_members_free_in_mock(self):
        client = MockGraphClient()
        result = run(client.get_free_busy(EMAILS, START, END))
        for email, blocks in result.items():
            assert blocks == [], f"{email} should be free"

    def test_single_member(self):
        client = MockGraphClient()
        result = run(client.get_free_busy(["solo@relay.app"], START, END))
        assert "solo@relay.app" in result

    def test_empty_member_list(self):
        client = MockGraphClient()
        result = run(client.get_free_busy([], START, END))
        assert result == {}


class TestMockGraphClientGetEvent:
    def test_get_event_returns_event_name(self):
        client = MockGraphClient()
        result = run(client.get_event("any-event-id"))
        assert "event_name" in result
        assert isinstance(result["event_name"], str)

    def test_get_event_returns_meeting_date(self):
        client = MockGraphClient()
        result = run(client.get_event("any-event-id"))
        assert "meeting_date" in result

    def test_get_event_with_none_id(self):
        client = MockGraphClient()
        result = run(client.get_event(None))
        assert "event_name" in result

    def test_no_real_graph_calls(self):
        # MockGraphClient never makes HTTP calls — no network fixture needed.
        # This test documents and enforces that invariant.
        import inspect
        source = inspect.getsource(MockGraphClient)
        assert "httpx" not in source
        assert "requests" not in source
        assert "aiohttp" not in source
