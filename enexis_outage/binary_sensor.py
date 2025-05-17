"""Binary sensor for Enexis outage status."""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_ZIPCODE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Enexis outage binary sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    zipcode = entry.data[CONF_ZIPCODE]

    async_add_entities([EnexisOutageBinarySensor(coordinator, zipcode)], True)


class EnexisOutageBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Binary sensor for Enexis outage status."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_has_entity_name = True

    def __init__(self, coordinator, zipcode):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._zipcode = zipcode
        self._attr_unique_id = f"enexis_outage_{zipcode}"
        self._attr_name = f"Enexis Outage {zipcode}"

    @property
    def is_on(self):
        """Return True if there's an outage."""
        if not self.coordinator.data:
            return False
        return self.coordinator.data.get("outage", False)

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        if not self.coordinator.data:
            return {"message": "Unknown"}
            
        return {
            "zipcode": self._zipcode,
            "message": self.coordinator.data.get("message", "Unknown"),
            "last_updated": self.coordinator.last_update_success_time.isoformat() if self.coordinator.last_update_success_time else None,
        }
