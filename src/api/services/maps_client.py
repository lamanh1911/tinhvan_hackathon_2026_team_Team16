from datetime import datetime
from typing import Protocol

# TODO: Implement GoogleMapsClient using Distance Matrix API when
# GOOGLE_MAPS_API_KEY is available. Auth: API key in request param.
# Endpoint: https://maps.googleapis.com/maps/api/distancematrix/json
# Pass departure_time for traffic-aware estimates.

_MOCK_TRAVEL_MINUTES = 30


class MapsClientProtocol(Protocol):
    async def get_travel_time(
        self,
        origin: str,
        destination: str,
        departure_time: datetime,
    ) -> int:
        """Return estimated travel time in minutes."""
        ...


class MockMapsClient:
    async def get_travel_time(
        self,
        origin: str,
        destination: str,
        departure_time: datetime,
    ) -> int:
        return _MOCK_TRAVEL_MINUTES


def make_maps_client(use_mocks: bool, settings=None) -> MapsClientProtocol:
    # TODO: When GoogleMapsClient is implemented, check settings.google_maps_api_key here
    # and return GoogleMapsClient(settings.google_maps_api_key) if available.
    return MockMapsClient()
