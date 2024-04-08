"""Platform for switch integration."""

from __future__ import annotations

from dateutil import parser

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .config_flow import NotPermitted
from .const import CONF_LOCK_ID, DOMAIN
from .coordinator import ChasterDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    chaster_coordinator: ChasterDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.data[CONF_LOCK_ID]
    ]

    async_add_entities(
        [
            LockIsFrozenSwitch(config_entry, chaster_coordinator),
        ]
    )


class LockIsFrozenSwitch(CoordinatorEntity, SwitchEntity):
    """Represents the frozen state of the lock."""

    _attr_icon = "mdi:snowflake-check"

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_name = f"{config_entry.title} Is Timer Frozen"
        self._attr_unique_id = f"{config_entry.title}_freeze"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_LOCK_ID])},
            name=config_entry.title,
            serial_number=config_entry.data[CONF_LOCK_ID],
        )

    def turn_on(self, **kwargs: parser.Any) -> None:
        """Set Lock to Frozen."""
        try:
            self.coordinator.chaster_client.set_lock_is_frozen(True)
        except NotPermitted as err:
            raise HomeAssistantError("Not allowed to change freeze state") from err

    def turn_off(self, **kwargs: parser.Any) -> None:
        """Set Lock to Not Frozen."""
        try:
            self.coordinator.chaster_client.set_lock_is_frozen(False)
        except NotPermitted as err:
            raise HomeAssistantError("Not allowed to change freeze state") from err

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.is_on = self.coordinator.data["isFrozen"]
        self.async_write_ha_state()
