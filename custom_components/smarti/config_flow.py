import logging
from homeassistant import config_entries
import voluptuous as vol
import aiohttp
from .const import DOMAIN  # Ensure const.py defines DOMAIN

_LOGGER = logging.getLogger(__name__)

async def validate_token_and_get_pat(email, token, integration):
    """Validate the token with the backend and return the GitHub PAT on success."""
    url = "https://smarti.pythonanywhere.com/validate-token"
    payload = {"email": email, "token": token, "integration": integration}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        _LOGGER.info(f"Validation successful for {integration}.")
                        return data.get("github_pat")
                else:
                    _LOGGER.error(f"Validation failed for {integration}: {response.status}")
    except aiohttp.ClientError as e:
        _LOGGER.error(f"Error validating subscription for {integration}: {e}")

    return None  # Return None if validation fails

@config_entries.HANDLERS.register(DOMAIN)
class SmartiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMARTi."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration screen."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            token = user_input["token"]
            version = user_input["version"]
            mode = user_input["mode"]

            # Validate the token with the backend
            github_pat = await validate_token_and_get_pat(email, token, version)
            if github_pat:
                # Success! Create the entry with all data
                _LOGGER.info("Configuration entry for SMARTi created successfully.")
                return self.async_create_entry(
                    title="SMARTi",
                    data={
                        "email": email,
                        "token": token,
                        "version": version,
                        "mode": mode,
                        "github_pat": github_pat,
                    },
                )
            else:
                errors["base"] = "invalid_token"

        # Define the schema for the form
        schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("token"): str,
            vol.Required("version", default="basic"): vol.In(["basic", "pro"]),
            vol.Required("mode", default="automatic"): vol.In(["automatic", "manual"]),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
