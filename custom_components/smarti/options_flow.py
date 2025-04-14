import logging
import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN
from . import validate_token_and_get_pat

_LOGGER = logging.getLogger(__name__)

class SmartiOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SMARTi re-authentication."""

    def __init__(self, config_entry):
        self.config_entry = config_entry
        self.errors = {}

    async def async_step_init(self, user_input=None):
        """Re-authentication entry form."""
        if user_input is not None:
            email = user_input["email"]
            token = user_input["token"]
            version = self.config_entry.data.get("version", "basic")

            github_pat = await validate_token_and_get_pat(email, token, version)

            if github_pat:
                _LOGGER.info("Re-authentication successful. Updating config entry.")
                new_data = {
                    **self.config_entry.data,
                    "email": email,
                    "token": token,
                    "github_pat": github_pat,
                }

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                return self.async_create_entry(title="", data={})
            else:
                self.errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("email", default=self.config_entry.data.get("email", "")): str,
            vol.Required("token"): str,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=self.errors,
        )
