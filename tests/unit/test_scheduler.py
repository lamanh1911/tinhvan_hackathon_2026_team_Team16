"""Unit tests — schedule slot logic (FR-03, FR-04).

Tests cover _has_conflict, _needs_travel_buffer, _next_business_days.
No database, no server required.
"""
from datetime import date, datetime, timedelta, timezone

import pytest

from src.api.routers.schedule import (
    _has_conflict,
    _needs_travel_buffer,
    _next_business_days,
)


def dt(hour: int, minute: int = 0, day: int = 16) -> datetime:
    """Helper: 2026-06-<day> HH:MM UTC."""
    return datetime(2026, 6, day, hour, minute, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# _next_business_days
# ---------------------------------------------------------------------------

class TestNextBusinessDays:
    def test_skips_saturday(self):
        # 2026-06-20 is Saturday
        days = _next_business_days(date(2026, 6, 20), 1)
        assert days[0].weekday() < 5

    def test_skips_sunday(self):
        # 2026-06-21 is Sunday
        days = _next_business_days(date(2026, 6, 21), 1)
        assert days[0].weekday() < 5

    def test_returns_correct_count(self):
        days = _next_business_days(date(2026, 6, 15), 5)
        assert len(days) == 5

    def test_all_business_days(self):
        days = _next_business_days(date(2026, 6, 15), 10)
        for d in days:
            assert d.weekday() < 5


# ---------------------------------------------------------------------------
# _has_conflict
# ---------------------------------------------------------------------------

class TestHasConflict:
    EMAILS = ["alice@relay.app", "bob@relay.app"]

    def _busy(self, email: str, start: datetime, end: datetime) -> dict[str, list[dict]]:
        return {email: [{"start": start.isoformat(), "end": end.isoformat()}]}

    def test_no_busy_no_conflict(self):
        busy = {e: [] for e in self.EMAILS}
        assert _has_conflict(dt(9), dt(10), self.EMAILS, busy) is False

    def test_exact_overlap_is_conflict(self):
        busy = self._busy("alice@relay.app", dt(9), dt(10))
        assert _has_conflict(dt(9), dt(10), self.EMAILS, busy) is True

    def test_partial_overlap_start_is_conflict(self):
        busy = self._busy("alice@relay.app", dt(8, 30), dt(9, 30))
        assert _has_conflict(dt(9), dt(10), self.EMAILS, busy) is True

    def test_partial_overlap_end_is_conflict(self):
        busy = self._busy("alice@relay.app", dt(9, 30), dt(10, 30))
        assert _has_conflict(dt(9), dt(10), self.EMAILS, busy) is True

    def test_adjacent_before_no_conflict(self):
        # Slot 10:00-11:00, busy 9:00-10:00 — adjacent but no overlap
        busy = self._busy("alice@relay.app", dt(9), dt(10))
        assert _has_conflict(dt(10), dt(11), self.EMAILS, busy) is False

    def test_conflict_on_second_member(self):
        busy = {"alice@relay.app": [], "bob@relay.app": [{"start": dt(9).isoformat(), "end": dt(10).isoformat()}]}
        assert _has_conflict(dt(9), dt(10), self.EMAILS, busy) is True

    def test_no_conflict_when_busy_after_slot(self):
        busy = self._busy("alice@relay.app", dt(11), dt(12))
        assert _has_conflict(dt(9), dt(10), self.EMAILS, busy) is False


# ---------------------------------------------------------------------------
# _needs_travel_buffer  (BR-11)
# ---------------------------------------------------------------------------

class TestNeedsTravelBuffer:
    EMAILS = ["alice@relay.app"]

    def test_no_prior_busy_no_buffer_needed(self):
        busy = {"alice@relay.app": []}
        assert _needs_travel_buffer(dt(9), self.EMAILS, busy, 30) is False

    def test_prior_block_too_close_needs_buffer(self):
        # Previous meeting ends at 8:45, slot starts 9:00 — only 15 min gap, need 30
        busy = {"alice@relay.app": [
            {"start": dt(8, 0).isoformat(), "end": dt(8, 45).isoformat()}
        ]}
        assert _needs_travel_buffer(dt(9), self.EMAILS, busy, 30) is True

    def test_sufficient_buffer_ok(self):
        # Previous meeting ends at 8:00, slot starts 9:00 — 60 min gap, need 30
        busy = {"alice@relay.app": [
            {"start": dt(7, 0).isoformat(), "end": dt(8, 0).isoformat()}
        ]}
        assert _needs_travel_buffer(dt(9), self.EMAILS, busy, 30) is False

    def test_exact_buffer_ok(self):
        # Previous meeting ends at 8:30, slot starts 9:00 — exactly 30 min gap
        busy = {"alice@relay.app": [
            {"start": dt(7, 0).isoformat(), "end": dt(8, 30).isoformat()}
        ]}
        assert _needs_travel_buffer(dt(9), self.EMAILS, busy, 30) is False

    def test_future_block_not_counted(self):
        # Upcoming meeting, not prior — should not trigger buffer
        busy = {"alice@relay.app": [
            {"start": dt(10).isoformat(), "end": dt(11).isoformat()}
        ]}
        assert _needs_travel_buffer(dt(9), self.EMAILS, busy, 30) is False
