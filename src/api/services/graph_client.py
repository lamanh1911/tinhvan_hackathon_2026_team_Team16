import logging
from typing import Protocol

logger = logging.getLogger(__name__)

_MOCK_EVENT: dict = {
    "event_name": "Q3 Partnership Meeting",
    "meeting_date": "2026-06-15",
}


class GraphClientProtocol(Protocol):
    async def get_event(self, graph_event_id: str | None) -> dict: ...


class MockGraphClient:
    async def get_event(self, graph_event_id: str | None) -> dict:
        logger.info("[MockGraphClient.get_event] graph_event_id=%s", graph_event_id)
        return dict(_MOCK_EVENT)


def make_graph_client(use_mocks: bool) -> GraphClientProtocol:
    return MockGraphClient()
