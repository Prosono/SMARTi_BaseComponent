import logging
import aiohttp
from datetime import timedelta
import os
import shutil

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval

from .const import DOMAIN
from .updater import update_files

_LOGGER = logging.getLogger(__name__)

# Interval for periodic updates (e.g., every hour)
UPDATE_INTERVAL = timedelta(hours=1)

# Paths to clean up
PATHS_TO_CLEAN = [
    "/config/packages/smartipackages",
    "/config/themes/smarti_themes/",
    "/config/smartidashboards/",
    "/config/www/images/smarti_images/",
    "/config/www/smarticards/",
    "/config/www/smartianimations/",
    "/config/www/smartilicense/",
]

# We'll define a short timeout for API calls
TIMEOUT = aiohttp.ClientTimeout(total=10)

async def validate_token_and_get_pat(email, token, integration):
    """
    Validate the token with the backend and return a fresh GitHub PAT
    on success. If validation fails, return None.
    """
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
                        _LOGGER.error(f"Validation error data: {data}")
                else:
                    _LOGGER.error(f"Validation failed for {integration}: {response.status}")
    except aiohttp.ClientError as e:
        _LOGGER.error(f"Error validating token for {integration}: {e}")

    return None  # Return None if validation fails

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SMARTi integration (YAML-based)."""
    _LOGGER.info("Setting up the SMARTi integration (YAML).")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SMARTi from a config entry."""
    _LOGGER.info("Setting up SMARTi from config entry.")

    # Make sure the domain data dict exists
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {}

    # Grab stored config data (from config_flow)
    config_data = entry.data
    email = config_data.get("email")
    token = config_data.get("token")
    version = config_data.get("version", "basic")  # "basic" or "pro"

    # 1) Fetch a *fresh* GitHub PAT on setup/reload
    new_pat = await validate_token_and_get_pat(email, token, version)
    if not new_pat:
        _LOGGER.warning("Could not get a NEW GitHub PAT. Using existing one.")
        github_pat = config_data.get("github_pat")
    else:
        _LOGGER.info("Fetched a NEW GitHub PAT.")
        github_pat = new_pat

        # Overwrite the stored token so we don’t lose it next time we restart
        new_data = {**config_data, "github_pat": github_pat}
        hass.config_entries.async_update_entry(entry, data=new_data)

    # Start the aiohttp session
    session = aiohttp.ClientSession()

    # 2) Periodic update function, which uses the (new) pat
    async def periodic_update(_):
        _LOGGER.info("Running periodic update for SMARTi integration.")
        await update_files(session, config_data, github_pat)

    # 3) Schedule periodic updates
    job = async_track_time_interval(hass, periodic_update, UPDATE_INTERVAL)
    hass.data[DOMAIN][entry.entry_id]["update_job"] = job
    hass.data[DOMAIN][entry.entry_id]["session"] = session

    # 4) Run initial update (with fresh pat if we have it)
    await update_files(session, config_data, github_pat)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Unloading SMARTi config entry.")

    # Cancel periodic updates
    update_job = hass.data[DOMAIN][entry.entry_id].get("update_job")
    if update_job:
        update_job()

    # Close the aiohttp session
    session = hass.data[DOMAIN][entry.entry_id].get("session")
    if session:
        await session.close()

    # Remove entry data
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle cleanup when the SMARTi integration is uninstalled."""
    _LOGGER.info("Cleaning up directories for SMARTi integration.")

    for path in PATHS_TO_CLEAN:
        if os.path.exists(path):
            try:
                shutil.rmtree(path)
                _LOGGER.info(f"Deleted directory: {path}")
            except Exception as e:
                _LOGGER.error(f"Failed to delete directory {path}: {e}")
        else:
            _LOGGER.info(f"Directory {path} does not exist, skipping.")

    _LOGGER.info("Cleanup completed for SMARTi integration.")

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle migration of the config entry if needed."""
    _LOGGER.info(f"Migrating SMARTi entry from version {entry.version}")

    current_version = 1

    if entry.version == current_version:
        _LOGGER.info("No migration necessary")
        return True

    # Implement migration logic if needed
    hass.config_entries.async_update_entry(entry, version=current_version)
    _LOGGER.info(f"Migration to version {current_version} successful")
    return True
