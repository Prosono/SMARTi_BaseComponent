import logging
from homeassistant import config_entries
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class SmartiUpdaterFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMARTi."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Automatically create the config entry without any user input."""
        try:
            _LOGGER.info("Creating SMARTi config entry with default values.")
            
            # Create the entry directly with default data (empty dictionary in this case)
            return self.async_create_entry(title="SMARTi", data={})

        except Exception as e:
            _LOGGER.error(f"Error in config flow: {e}", exc_info=True)  # Log full stack trace
            return self.async_abort(reason="unknown_error")
