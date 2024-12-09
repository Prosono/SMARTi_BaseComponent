import logging
from homeassistant import config_entries
import voluptuous as vol
import homeassistant.helpers.config_validation as cv  # Import config validation
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class SmartiUpdaterFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMARTi."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        try:
            if user_input is not None:
                _LOGGER.info(f"User input received: {user_input}")
                # When the user submits the form, create the entry
                return self.async_create_entry(title="SMARTi", data=user_input)

            # If no input, show the form with proper Boolean fields
            _LOGGER.info("Displaying the config flow form")

            schema = vol.Schema({
                vol.Optional("update_node_red", default=False): cv.boolean,
                vol.Optional("update_dashboards", default=False): cv.boolean,
                vol.Optional("update_automations", default=False): cv.boolean,
            })

            _LOGGER.debug(f"Schema being used: {schema}")

            return self.async_show_form(
                step_id="user",
                data_schema=schema,
                description_placeholders={"name": "SMARTi"},
            )
        except Exception as e:
            _LOGGER.error(f"Error in config flow: {e}", exc_info=True)  # Log full stack trace
            return self.async_abort(reason="unknown_error")
