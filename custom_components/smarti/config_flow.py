import logging
from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class SmartiUpdaterFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMARTi."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            email = user_input.get("email")
            api_token = user_input.get("api_token")

            # Validate the subscription
            if not await self._validate_subscription(email):
                errors["email"] = "invalid_subscription"
            elif not await self._validate_token(api_token):
                errors["api_token"] = "invalid_token"
            else:
                return self.async_create_entry(title="SMARTi", data=user_input)

        schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("api_token"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _validate_subscription(self, email):
        """Validate the subscription using your backend."""
        # Replace this with the actual validation logic
        _LOGGER.debug(f"Validating subscription for {email}")
        return True

    async def _validate_token(self, api_token):
        """Validate the GitHub API token."""
        headers = {"Authorization": f"Bearer {api_token}"}
        async with self.hass.helpers.aiohttp_client.async_get_clientsession().get(
            "https://api.github.com/user", headers=headers
        ) as response:
            return response.status == 200
