"""Platform for sensor integration."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_LOCK_ID, DOMAIN
from .coordinator import ChasterDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    chaster_coordinator: ChasterDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.data[CONF_LOCK_ID]
    ]
    async_add_entities([LockIsFrozenSensor(config_entry, chaster_coordinator)])


class LockIsFrozenSensor(CoordinatorEntity, BinarySensorEntity):
    """Represents the frozen state of the lock."""

    _attr_icon = "mdi:snowflake"

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = f"{config_entry.title} Frozen"
        self._attr_unique_id = f"{config_entry.title}_frozen"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config_entry.data[CONF_LOCK_ID])},
            name=config_entry.title,
            serial_number=config_entry.data[CONF_LOCK_ID],
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.is_on = self.coordinator.data["isFrozen"]
        self.async_write_ha_state()
