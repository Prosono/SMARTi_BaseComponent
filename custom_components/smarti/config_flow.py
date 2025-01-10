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
            email = user_input["email"]
            version = user_input["version"]
            mode = user_input["mode"]

            # Save the selected version, email, and mode for the next step
            self.version = version
            self.email = email
            self.mode = mode

            # Move to the token step
            return await self.async_step_token()

        # Define the schema for the form
        schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("version", default="basic"): vol.In(["basic", "pro"]),
            vol.Required("mode", default="automatic"): vol.In(["automatic", "manual"]),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_token(self, user_input=None):
        """Handle token input or generation based on the selected version."""
        errors = {}

        if user_input is not None:
            if self.version == "basic" and user_input.get("generate_token"):
                # Generate a token for Basic users
                token = await generate_token(self.email)
                if token:
                    _LOGGER.info("Token generated for Basic version.")
                    github_pat = await validate_token_and_get_pat(self.email, token, "basic")
                    if github_pat:
                        _LOGGER.info("Token validated successfully. Integration is ready to use.")
                        return self.async_create_entry(
                            title="SMARTi Basic",
                            data={
                                "email": self.email,
                                "basic_token": token,
                                "version": self.version,
                                "mode": self.mode,
                                "github_pat": github_pat,
                            },
                        )
                    else:
                        errors["base"] = "invalid_token"
                else:
                    errors["base"] = "token_generation_failed"
            elif self.version == "pro":
                # Validate the provided Pro token
                pro_token = user_input.get("pro_token")
                github_pat = await validate_token_and_get_pat(self.email, pro_token, "pro")
                if github_pat:
                    _LOGGER.info("Token validated successfully. Integration is ready to use.")
                    return self.async_create_entry(
                        title="SMARTi Pro",
                        data={
                            "email": self.email,
                            "pro_token": pro_token,
                            "version": self.version,
                            "mode": self.mode,
                            "github_pat": github_pat,
                        },
                    )
                else:
                    errors["base"] = "invalid_token"

        # Define the schema for the form
        if self.version == "basic":
            # Basic version allows generating a token
            schema = vol.Schema({
                vol.Optional("generate_token", default=True): bool,  # Add a button-like checkbox
            })
            return self.async_show_form(
                step_id="token",
                data_schema=schema,
                description_placeholders={
                    "message": (
                        "Click below to generate a token for the Basic version. "
                        "The token will be sent to your email."
                    )
                },
                errors=errors,
            )
        else:
            # Pro version requires a token input
            schema = vol.Schema({
                vol.Required("pro_token"): str,
            })
            return self.async_show_form(
                step_id="token",
                data_schema=schema,
                description_placeholders={
                    "message": (
                        "Please enter the token you received after purchasing SMARTi Pro.<br>"
                        "Do you want to upgrade to the PRO version? "
                        "Purchase a subscription here: <a href='https://www.smarti.dev' target='_blank'>https://www.smarti.dev</a>"
                    )
                },
                errors=errors,
            )
