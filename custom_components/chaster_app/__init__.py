"""The chaster.app integration."""

from __future__ import annotations

import logging
from typing import List

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, HomeAssistantError, ServiceCall
import homeassistant.helpers.config_validation as cv
import homeassistant.helpers.device_registry as dr
from homeassistant.helpers.typing import ConfigType

from .chaster_client import ChasterClient
from .config_flow import NotPermitted
from .const import CONF_API_TOKEN, CONF_LOCK_ID, DOMAIN, SERVICE_UPDATE_LOCK_DURATION
from .coordinator import ChasterDataUpdateCoordinator

PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR, Platform.SWITCH]

_LOGGER = logging.getLogger(__name__)


def setup(hass: HomeAssistant) -> bool:
    """Set up chaster.app."""

    async def handle_update_lock_duration(call: ServiceCall):
        """Handle the service call."""
        device_id: str = call.data.get("device_id", None)
        time_to_modify: int = call.data.get("duration", None)

        if device_id is None:
            raise HomeAssistantError("device_id must be provided.")

        device_registry = dr.async_get(hass)
        device_entry = device_registry.async_get(device_id)

        if device_entry is None:
            raise HomeAssistantError("device not found in registry")

        lock_id = device_entry.serial_number
        if time_to_modify is None:
            raise HomeAssistantError(
                "duration must be provided as a number in minutes."
            )

        chaster_coordinator: ChasterDataUpdateCoordinator = hass.data[DOMAIN][
            device_entry.serial_number
        ]
        if chaster_coordinator is None:
            raise HomeAssistantError(f"lock with id {lock_id} not found")

        try:
            await hass.async_add_executor_job(
                chaster_coordinator.chaster_client.update_lock_time, time_to_modify
            )
        except NotPermitted as err:
            if err.args == "not permitted to remove time":
                raise HomeAssistantError(
                    "Not allowed to remove time from locked duration"
                ) from err
            raise HomeAssistantError("Not allowed to change duration") from err

    hass.services.register(
        DOMAIN,
        SERVICE_UPDATE_LOCK_DURATION,
        handle_update_lock_duration,
        schema=vol.Schema(
            vol.All(
                {
                    vol.Required("device_id"): str,
                    vol.Required("duration"): int,
                }
            )
        ),
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up chaster.app from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # TODO 1. Create API instance
    # TODO 2. Validate the API connection (and authentication)
    # TODO 3. Store an API object for your platforms to access
    # hass.data[DOMAIN][entry.entry_id] = MyApi(...)
    data_coordinator = ChasterDataUpdateCoordinator(
        hass, ChasterClient(entry.data[CONF_LOCK_ID], entry.data[CONF_API_TOKEN])
    )
    await data_coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.data[CONF_LOCK_ID]] = data_coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.data[CONF_LOCK_ID])

    return unload_ok
