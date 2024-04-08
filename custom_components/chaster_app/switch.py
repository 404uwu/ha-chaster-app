"""Platform for switch integration."""

from __future__ import annotations

from dateutil import parser

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ChasterDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    chaster_coordinator: ChasterDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        [
            LockIsFrozenSwitch(config_entry, chaster_coordinator),
        ]
    )


class LockIsFrozenSwitch(CoordinatorEntity, SwitchEntity):
    """Represents the frozen state of the lock."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:snowflake-check"

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_name = f"{config_entry.title} Is Timer Frozen"
        self._attr_unique_id = f"{config_entry.title}_freeze"

    def turn_on(self, **kwargs: parser.Any) -> None:
        """Set Lock to Frozen."""
        self.coordinator.chaster_client.set_lock_is_frozen(True)

    def turn_off(self, **kwargs: parser.Any) -> None:
        """Set Lock to Not Frozen."""
        self.coordinator.chaster_client.set_lock_is_frozen(False)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.is_on = self.coordinator.data["isFrozen"]
        self.async_write_ha_state()


class LockTotalLockedDurationSensor(CoordinatorEntity, SensorEntity):
    """Represents the total locked duration of the lock."""

    _attr_native_unit_of_measurement = "ms"
    _attr_device_class = SensorDeviceClass.DURATION

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_name = f"{config_entry.title} Total Locked Duration"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        total_duration_hours = self.coordinator.data["totalDuration"]
        self._attr_native_value = total_duration_hours

        self.async_write_ha_state()
