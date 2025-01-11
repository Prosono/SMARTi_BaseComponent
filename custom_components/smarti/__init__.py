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
from .helpers import validate_token_and_get_pat  # Import the helper for token validation

_LOGGER = logging.getLogger(__name__)

# Interval for periodic updates (e.g., every hour)
UPDATE_INTERVAL = timedelta(hours=1)

# Interval for periodic token validation (e.g., every 24 hours)
VALIDATION_INTERVAL = timedelta(hours=24)

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

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SMARTi integration."""
    _LOGGER.info("Setting up the SMARTi integration.")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SMARTi from a config entry."""
    _LOGGER.info("Setting up SMARTi from config entry.")

    # Store domain data
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {}

    # Start the aiohttp session for GitHub API requests
    session = aiohttp.ClientSession()
    github_pat = entry.data.get("github_pat")
    config_data = entry.data
    email = config_data.get("email")
    token = config_data.get("token")
    version = config_data.get("version")  # 'basic' or 'pro'

    # Define the periodic update function
    async def periodic_update(_):
        _LOGGER.info("Running periodic update for SMARTi integration.")
        await update_files(session, config_data, github_pat)

    # Define the periodic token validation function
    async def periodic_validation(_):
        _LOGGER.info("Running periodic token validation for SMARTi integration.")

        # Validate the token
        is_valid = await validate_token_and_get_pat(email, token, version)
        if not is_valid:
            _LOGGER.error("Token is invalid or expired. Pausing updates until reconfigured.")
            hass.services.async_call(
                "persistent_notification",
                "create",
                {
                    "title": "SMARTi Token Expired",
                    "message": f"Your {version.capitalize()} token is invalid or expired. Please reconfigure the integration for a Basic token or upgrade to a Pro token.",
                    "notification_id": "smarti_token_error",
                },
            )
            return  # Skip further updates until reconfigured

        _LOGGER.info("Token validation successful.")

    # Schedule periodic updates
    hass.data[DOMAIN][entry.entry_id]["update_job"] = async_track_time_interval(
        hass, periodic_update, UPDATE_INTERVAL
    )

    # Schedule periodic token validation
    hass.data[DOMAIN][entry.entry_id]["validation_job"] = async_track_time_interval(
        hass, periodic_validation, VALIDATION_INTERVAL
    )

    # Run the initial update
    await update_files(session, config_data, github_pat)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Unloading SMARTi config entry.")

    # Cancel periodic updates
    update_job = hass.data[DOMAIN][entry.entry_id].get("update_job")
    if update_job:
        update_job()

    # Cancel periodic token validation
    validation_job = hass.data[DOMAIN][entry.entry_id].get("validation_job")
    if validation_job:
        validation_job()

    # Close the aiohttp session
    session = aiohttp.ClientSession()
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
                shutil.rmtree(path)  # Recursively delete the directory and its contents
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
