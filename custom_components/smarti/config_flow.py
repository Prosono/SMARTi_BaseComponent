import logging
from homeassistant import config_entries
import voluptuous as vol
import aiohttp
from .const import DOMAIN  # Replace with your actual `const` file

_LOGGER = logging.getLogger(__name__)

@config_entries.HANDLERS.register(DOMAIN)
class SmartiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMARTi."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            token = user_input["token"]

            # Validate the token and get the GitHub PAT
            github_pat = await validate_token_and_get_pat(email, token)
            if github_pat:
                # Store the GitHub PAT in the config entry
                return self.async_create_entry(
                    title="SMARTi",
                    data={"email": email, "token": token, "github_pat": github_pat},
                )
            else:
                errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("token"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def _validate_subscription(self, email, token):
        """Validate the email and token with the backend server."""
        url = "https://your-backend-url/validate-token"
        payload = {"email": email, "token": token}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        _LOGGER.info("Subscription validated successfully.")
                        return True
                    else:
                        _LOGGER.error(f"Subscription validation failed: {response.status}")
                        return False
        except aiohttp.ClientError as e:
            _LOGGER.error(f"Error validating subscription: {e}")
            return False
