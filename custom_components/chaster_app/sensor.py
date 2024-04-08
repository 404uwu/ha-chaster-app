"""Platform for sensor integration."""

from __future__ import annotations

from datetime import datetime

from dateutil import parser

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
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
    """Set up the sensor platform."""
    chaster_coordinator: ChasterDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    async_add_entities(
        [
            LockUnlockTimeSensor(config_entry, chaster_coordinator),
            LockUnlockDurationSensor(config_entry, chaster_coordinator),
            LockTotalLockedDurationSensor(config_entry, chaster_coordinator),
        ]
    )


class LockUnlockTimeSensor(CoordinatorEntity, SensorEntity):
    """Represents the unlock date of the lock."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:calendar-blank"

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_name = f"{config_entry.title} Unlock Date"
        self._attr_unique_id = f"{config_entry.title}_unlock_date"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        end_date = self.coordinator.data["endDate"]
        if not end_date:
            self._attr_native_value = None
        else:
            self._attr_native_value = parser.parse(end_date)

        self.async_write_ha_state()


class LockUnlockDurationSensor(CoordinatorEntity, SensorEntity):
    """Represents the time until the unlock date of the lock."""

    _attr_native_unit_of_measurement = "h"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:timer-sand-complete"

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_name = f"{config_entry.title} Duration Until Unlock Date"
        self._attr_unique_id = f"{config_entry.title}_duration_until_unlock_date"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        end_date = self.coordinator.data["endDate"]
        if not end_date:
            self._attr_native_value = None
        else:
            parsed_end_date = parser.parse(end_date)
            self._attr_native_value = (
                (parsed_end_date - datetime.now(parsed_end_date.tzinfo)).seconds
                / 60
                / 60
            )

        self.async_write_ha_state()


class LockTotalLockedDurationSensor(CoordinatorEntity, SensorEntity):
    """Represents the total locked duration of the lock."""

    _attr_native_unit_of_measurement = "h"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_icon = "mdi:timer"

    def __init__(
        self, config_entry: ConfigEntry, coordinator: ChasterDataUpdateCoordinator
    ) -> None:
        super().__init__(coordinator)

        self.coordinator = coordinator
        self._attr_name = f"{config_entry.title} Total Locked Duration"
        self._attr_unique_id = f"{config_entry.title}_total_locked_unlock"

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        total_duration_hours = self.coordinator.data["totalDuration"] / 1000 / 60 / 60
        self._attr_native_value = total_duration_hours

        self.async_write_ha_state()
