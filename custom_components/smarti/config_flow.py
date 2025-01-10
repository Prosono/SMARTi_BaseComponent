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
        """Initial step: Select Basic or Pro."""
        errors = {}

        if user_input is not None:
            self.version = user_input["version"]

            if self.version == "basic":
                return await self.async_step_basic_token_choice()
            else:  # Pro
                return await self.async_step_pro_link()

        schema = vol.Schema({
            vol.Required("version", default="basic"): vol.In(["basic", "pro"]),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_basic_token_choice(self, user_input=None):
        """Step for Basic: Ask if the user has generated a token."""
        errors = {}

        if user_input is not None:
            if user_input["has_token"] == "no":
                return await self.async_step_generate_token()
            else:
                return await self.async_step_basic_token_input()

        schema = vol.Schema({
            vol.Required("has_token", default="no"): vol.In(["yes", "no"]),
        })

        return self.async_show_form(
            step_id="basic_token_choice",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_generate_token(self, user_input=None):
        """Step for Basic: Generate a token."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            token = await generate_token(email)
            if token:
                _LOGGER.info("Token generated successfully.")
                self.email = email
                self.token = token
                return await self.async_step_basic_token_input()
            else:
                errors["base"] = "token_generation_failed"

        schema = vol.Schema({
            vol.Required("email"): str,
        })

        return self.async_show_form(
            step_id="generate_token",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_basic_token_input(self, user_input=None):
        """Step for Basic: Input the token."""
        errors = {}

        if user_input is not None:
            token = user_input["basic_token"]
            github_pat = await validate_token_and_get_pat(self.email, token, "basic")
            if github_pat:
                _LOGGER.info("Token validated successfully. Integration is ready to use.")
                self.github_pat = github_pat
                return await self.async_step_mode()
            else:
                errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("basic_token", default=self.token if hasattr(self, "token") else ""): str,
        })

        return self.async_show_form(
            step_id="basic_token_input",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_pro_link(self, user_input=None):
        """Step for Pro: Provide a purchase link."""
        if user_input is not None:
            # Redirect to the Pro token input step
            return await self.async_step_pro_token_input()

        # Show the form with the purchase link
        return self.async_show_form(
            step_id="pro_link",
            data_schema=vol.Schema({}),  # No input fields here
            description_placeholders={
                "link": "<a href='https://www.smarti.dev' target='_blank'>Purchase SMARTi Pro</a>"
            },
        )


    async def async_step_pro_token_input(self, user_input=None):
        """Step for Pro: Input the token."""
        errors = {}

        if user_input is not None:
            token = user_input["pro_token"]
            github_pat = await validate_token_and_get_pat(self.email, token, "pro")
            if github_pat:
                _LOGGER.info("Token validated successfully. Integration is ready to use.")
                self.github_pat = github_pat
                return await self.async_step_mode()
            else:
                errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("pro_token"): str,
        })

        return self.async_show_form(
            step_id="pro_token_input",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_mode(self, user_input=None):
        """Step for selecting mode: Automatic or Manual."""
        errors = {}

        if user_input is not None:
            mode = user_input["mode"]
            return self.async_create_entry(
                title=f"SMARTi {self.version.capitalize()}",
                data={
                    "email": self.email,
                    "token": self.token,
                    "version": self.version,
                    "mode": mode,
                    "github_pat": self.github_pat,
                },
            )

        schema = vol.Schema({
            vol.Required("mode", default="automatic"): vol.In(["automatic", "manual"]),
        })

        return self.async_show_form(
            step_id="mode",
            data_schema=schema,
            description_placeholders={
                "automatic_description": "Files will automatically update.",
                "manual_description": "You control when files are updated.",
            },
            errors=errors,
        )
