import logging
from homeassistant import config_entries
import voluptuous as vol
import aiohttp
from .const import DOMAIN  # Ensure const.py defines DOMAIN
from .options_flow import SmartiOptionsFlowHandler

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

    def __init__(self):
        self.token = None
        self.github_pat = None
        self.email = None
        self.version = None

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
            if user_input["has_token"] == "yes":
                return await self.async_step_basic_token_input()
            else:
                return await self.async_step_generate_token()

        schema = vol.Schema({
            vol.Required("has_token", default="no"): vol.In(["yes", "no"]),
        })

        return self.async_show_form(
            step_id="basic_token_choice",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_generate_token(self, user_input=None):
        """Step for Basic: Generate a new token."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]

            # Generate or fetch a token
            token = await generate_token(email)
            if token:
                _LOGGER.info("Token generated successfully. Please check your email.")
                self.email = email
                self.token = token
                return await self.async_step_basic_token_input()  # Redirect to token input step for validation
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
        """Step for Basic: Input email and token."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            token = user_input["basic_token"]

            # Validate the provided token
            github_pat = await validate_token_and_get_pat(email, token, "basic")
            if github_pat:
                _LOGGER.info("Token validated successfully. Integration is ready to use.")
                self.email = email
                self.token = token
                self.github_pat = github_pat

                return await self.async_step_mode()
            else:
                errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("email"): str,
            vol.Required("basic_token"): str,
        })

        return self.async_show_form(
            step_id="basic_token_input",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_pro_link(self, user_input=None):
        """Step for Pro: Provide a purchase link."""
        if user_input is not None:
            return await self.async_step_pro_token_input()

        return self.async_show_form(
            step_id="pro_link",
            data_schema=vol.Schema({}),  # No input fields here
            description_placeholders={
                "link": "<a href='https://www.smarti.dev' target='_blank'>Purchase SMARTi Pro</a>"
            },
        )

    async def async_step_pro_token_input(self, user_input=None):
        """Step for Pro: Input email and token."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            token = user_input["pro_token"]

            github_pat = await validate_token_and_get_pat(email, token, "pro")
            if github_pat:
                _LOGGER.info("Token validated successfully. Integration is ready to use.")
                self.email = email
                self.token = token
                self.github_pat = github_pat

                return await self.async_step_mode()
            else:
                errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("email"): str,
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

            # 🔐 Enforce uniqueness here only
            await self.async_set_unique_id(self.email)
            self._abort_if_unique_id_configured()

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
                "automatic_description": "Automatic mode: This option puts your Home Assistant into YAML mode...",
                "manual_description": "Manual mode: This option keeps your Home Assistant as-is...",
            },
            errors=errors,
        )


    async def async_step_reauth(self, entry_data):
        """Start reauth flow by asking for updated credentials."""
        self.email = entry_data.get("email")
        self.version = entry_data.get("version")

        # Get the config entry object and store it in context
        entry = self.hass.config_entries.async_get_entry(entry_data["entry_id"])
        self._reauth_entry = entry

        _LOGGER.info(f"Reauth initiated for {self.email} ({self.version})")

        return await self.async_step_reauth_credentials()      

    async def async_step_reauth_credentials(self, user_input=None):
        """Collect new token and update existing config entry."""
        errors = {}

        if user_input is not None:
            email = user_input["email"]
            token = user_input["token"]
            version = self.version

            github_pat = await validate_token_and_get_pat(email, token, version)
            if github_pat:
                updated_data = {
                    **self._reauth_entry.data,
                    "email": email,
                    "token": token,
                    "github_pat": github_pat,
                }

                self.hass.config_entries.async_update_entry(
                    self._reauth_entry,
                    data=updated_data
                )
                return self.async_abort(reason="reauth_successful")
            else:
                errors["base"] = "invalid_token"

        schema = vol.Schema({
            vol.Required("email", default=self.email): str,
            vol.Required("token"): str,
        })

        return self.async_show_form(
            step_id="reauth_credentials",
            data_schema=schema,
            errors=errors,
        )
