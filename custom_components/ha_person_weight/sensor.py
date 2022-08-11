from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorStateClass, RestoreSensor
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.const import (
    CONF_NAME,
    CONF_MINIMUM,
    CONF_MAXIMUM,
    CONF_SENSORS,
    MASS_KILOGRAMS,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    ATTR_UNIT_OF_MEASUREMENT
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor."""
    config = entry.data
    sensor = WeightSensor(
        unique_id=entry.entry_id,
        name=config[CONF_NAME],
        min=config[CONF_MINIMUM],
        max=config[CONF_MAXIMUM],
        sensors=config[CONF_SENSORS]
    )
    async_add_entities([sensor])


class WeightSensor(RestoreSensor):

    def __init__(self, unique_id, name, min, max, sensors):
        self._unique_id = unique_id
        self._state = None
        self._name = name
        self._min = min
        self._max = max
        self._sensors = str(sensors).split(",")

        self._unit_of_measurement = None
        self._icon = "mdi:scale-bathroom"

        self._attr_extra_state_attributes = {
            "minimum": min,
            "maximum": max
        }

    @callback
    def _update_filter_sensor_state_event(self, event):
        """Handle device state changes."""
        new_state = event.data.get("new_state")

        if new_state.state in (STATE_UNKNOWN, STATE_UNAVAILABLE):
            return

        if self._unit_of_measurement is None:
            unit = new_state.attributes.get(ATTR_UNIT_OF_MEASUREMENT)
            self._unit_of_measurement = MASS_KILOGRAMS if unit is None else unit
            self._attr_state_class = SensorStateClass.MEASUREMENT

        value = new_state.state
        try:
            if int(value) >= self._min and int(value) <= self._max:
                self._state = value
                self.async_write_ha_state()
        except Exception as err:
            _LOGGER.warning("error:%s", err)

    async def async_added_to_hass(self):
        """Handle entity which will be added."""
        await super().async_added_to_hass()
        if (last_sensor_data := await self.async_get_last_sensor_data()) is not None:
            self._state = last_sensor_data.native_value
            if last_sensor_data.native_unit_of_measurement is not None:
                self._unit_of_measurement = last_sensor_data.native_unit_of_measurement
                self._attr_state_class = SensorStateClass.MEASUREMENT

        self.async_on_remove(
            async_track_state_change_event(
                self.hass, self._sensors, self._update_filter_sensor_state_event
            )
        )

    @property
    def unique_id(self):
        return self._unique_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def native_unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    @property
    def native_value(self):
        """Return the state of the resources."""
        return self._state
