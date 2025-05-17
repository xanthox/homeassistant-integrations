"""Config flow for Enexis Outage Status integration."""
import logging
import re
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, CONF_ZIPCODE

_LOGGER = logging.getLogger(__name__)


class EnexisOutageConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Enexis Outage Status."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            zipcode = user_input[CONF_ZIPCODE]
            
            # Validate the ZIP code format (4 digits followed by 2 letters)
            if not re.match(r"^\d{4}[A-Za-z]{2}$", zipcode):
                errors[CONF_ZIPCODE] = "invalid_zipcode"
            else:
                # Check if already configured
                await self.async_set_unique_id(zipcode)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=f"Outage Status for {zipcode}", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ZIPCODE): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return EnexisOutageOptionsFlow(config_entry)


class EnexisOutageOptionsFlow(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_ZIPCODE,
                        default=self.config_entry.data.get(CONF_ZIPCODE),
                    ): str,
                }
            ),
        )
