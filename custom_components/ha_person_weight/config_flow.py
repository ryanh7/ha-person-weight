from __future__ import annotations
import logging

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_NAME, CONF_MINIMUM, CONF_MAXIMUM, CONF_SENSORS

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class WeightFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Met Eireann component."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        errors = {}

        if user_input is not None:
            return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                    {
                        vol.Required(CONF_NAME): str,
                        vol.Required(CONF_MINIMUM, default=50): vol.All(
                            cv.positive_int, vol.Range(min=0, max=1000000)
                        ),
                        vol.Required(CONF_MAXIMUM, default=60): vol.All(
                            cv.positive_int, vol.Range(min=0, max=1000000)
                        ),
                        vol.Required(CONF_SENSORS): str,
                    }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.config = dict(config_entry.data)

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            self.config.update(user_input)
            self.hass.config_entries.async_update_entry(
                self.config_entry,
                data=self.config
            )
            await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=self.config)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                    {
                        vol.Required(CONF_MINIMUM, default=self.config[CONF_MINIMUM]): vol.All(
                            cv.positive_int, vol.Range(min=0, max=1000000)
                        ),
                        vol.Required(CONF_MAXIMUM, default=self.config[CONF_MAXIMUM]): vol.All(
                            cv.positive_int, vol.Range(min=0, max=1000000)
                        ),
                        vol.Required(CONF_SENSORS, default=self.config[CONF_SENSORS]): str,
                    }
            )
        )
