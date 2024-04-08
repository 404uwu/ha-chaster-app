"""DataUpdateCoordinator for chaster_app integration."""

from __future__ import annotations

from asyncio import timeout
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .chaster_client import ChasterClient

_LOGGER = logging.getLogger(__name__)


class ChasterDataUpdateCoordinator(DataUpdateCoordinator):
    """DataUpdateCoordinator for chaster_app integration."""

    def __init__(self, hass: HomeAssistant, chaster_client: ChasterClient) -> None:
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="My sensor",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
        )
        self.chaster_client = chaster_client

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            async with timeout(10):
                # Grab active context variables to limit data required to be fetched from API
                # Note: using context is not required if there is no need or ability to limit
                # data retrieved from API.
                return await self.hass.async_add_executor_job(
                    self.chaster_client.fetch_lock_details
                )
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}")
