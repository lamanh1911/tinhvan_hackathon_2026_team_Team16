import logging
from datetime import datetime
from typing import Protocol

logger = logging.getLogger(__name__)

_MOCK_EVENT: dict = {
    "event_name": "Q3 Partnership Meeting",
    "meeting_date": "2026-06-15",
}


class GraphClientProtocol(Protocol):
    async def get_event(self, graph_event_id: str | None) -> dict: ...

    async def get_free_busy(
        self,
        member_emails: list[str],
        start_dt: datetime,
        end_dt: datetime,
    ) -> dict[str, list[dict]]:
        """Return busy time blocks per email address.

        Each value is a list of {"start": ISO str, "end": ISO str} dicts.
        Empty list means the member is free for the entire window.
        """
        ...


class MockGraphClient:
    async def get_event(self, graph_event_id: str | None) -> dict:
        logger.info("[MockGraphClient.get_event] graph_event_id=%s", graph_event_id)
        return dict(_MOCK_EVENT)

    async def get_free_busy(
        self,
        member_emails: list[str],
        start_dt: datetime,
        end_dt: datetime,
    ) -> dict[str, list[dict]]:
        # Mock: no busy blocks — all members are free
        return {email: [] for email in member_emails}


def make_graph_client(use_mocks: bool) -> GraphClientProtocol:
    return MockGraphClient()
