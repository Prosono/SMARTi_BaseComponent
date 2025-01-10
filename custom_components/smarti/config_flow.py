import logging
from homeassistant import config_entries
import voluptuous as vol
import aiohttp
from .const import DOMAIN  # Ensure const.py defines DOMAIN

_LOGGER = logging.getLogger(__name__)

# Timeout for API calls
TIMEOUT = aiohttp.ClientTimeout(total=10)

async def validate_token_and_get_pat(email, token, integration):
    """Validate the token with the backend and return the GitHub PAT on success."""
    url = "https://smarti.pythonanywhere.com/validate-token"
    payload = {"email": email, "token": token, "integration": integration}

    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
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

async def generate_token(email):
    """Generate a token for Basic users by calling the backend."""
    url = "https://smarti.pythonanywhere.com/generate-token"
    payload = {"email": email}

    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("status") == "success":
                        _LOGGER.info("Token generated successfully. Please check your email.")
                        return data.get("token")
                else:
                    _LOGGER.error(f"Failed to generate token: {response.status}")
    except aiohttp.ClientError as e:
        _LOGGER.error(f"Error generating token: {e}")

    return None  # Return None if token generation fails

@config_entries.HANDLERS.register(DOMAIN)
class SmartiConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SMARTi."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial configuration screen."""
        errors = {}

        if user_input is not None:
            if user_input.get("generate_token_email"):
                email = user_input["generate_token_email"]
                # Generate a Basic token
                token = await generate_token(email)
                if token:
                    _LOGGER.info("Token generated successfully.")
                    return self.async_show_form(
                        step_id="user",
                        data_schema=vol.Schema({
                            vol.Required("email", default=""): str,
                            vol.Required("version", default="basic"): vol.In(["basic", "pro"]),
                            vol.Required("mode", default="automatic"): vol.In(["automatic", "manual"]),
                            vol.Optional("basic_token", default=token): str,
                            vol.Optional("generate_token_email", default=""): str,
                        }),
                        description_placeholders={
                            "message": (
                                f"A token has been sent to {email}. Please check your email."
                            )
                        },
                        errors=errors,
                    )
                else:
                    errors["base"] = "token_generation_failed"

            # Handle form submission for other fields
            email = user_input["email"]
            version = user_input["version"]
            mode = user_input["mode"]
            token = user_input.get("basic_token", "").strip()

            # Save the selected configuration
            self.version = version
            self.email = email
            self.mode = mode
            self.token = token

            # Validate the token directly if entered
            if token:
                github_pat = await validate_token_and_get_pat(email, token, version)
                if github_pat:
                    _LOGGER.info("Token validated successfully. Integration is ready to use.")
                    return self.async_create_entry(
                        title=f"SMARTi {version.capitalize()}",
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
            vol.Required("email", default=""): str,
            vol.Required("version", default="basic"): vol.In(["basic", "pro"]),
            vol.Required("mode", default="automatic"): vol.In(["automatic", "manual"]),
            vol.Optional("basic_token", default=""): str,  # Field for entering an existing Basic token
            vol.Optional("generate_token_email", default=""): str,  # Email field for generating a token
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            description_placeholders={
                "headline": "No token? Generate one for free for the Basic version.",
            },
            errors=errors,
        )
