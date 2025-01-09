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

# Paths and files to clean up
PATHS_TO_CLEAN = [
    "/config/packages/",
    "/config/themes/smarti_themes/",
    "/config/dashboards/",
    "/config/www/images/smarti_images/",
    "/config/www/community/",
    "/config/www/animations/",
    "/config/www/smartilicense/",
]

FILES_TO_DELETE = {
    "/config/packages/": [
        "smarti_custom_cards_package.yaml",
        "smarti_dashboard_package.yaml",
        "smarti_dashboard_settings.yaml",
        "smarti_dynamic_power_sensor_package.yaml",
        "smarti_general_automations.yaml",
        "smarti_general_package.yaml",
        "smarti_location_package.yaml",
        "smarti_navbar_package.yaml",
        "smarti_power_control_package.yaml",
        "smarti_power_price_package.yaml",
        "smarti_powerflow_gridfee_package.yaml",
        "smarti_template_sensors.yaml",
        "smarti_weather_package.yaml",
        "smarti_translation_package.yaml",
        "smarti_powerflow_gridfee_automations",
    ],
    "/config/dashboards/": [
        "smarti-custom-cards-test.yaml",
    ],
    "/config/themes/smarti_themes/": [],
    "/config/www/images/smarti_images/": [],
    "/config/www/community/": [],
    "/config/www/animations/": [],
    "/config/www/smartilicense/": [],
}

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

    # Define the periodic update function
    async def periodic_update(_):
        _LOGGER.info("Running periodic update for SMARTi integration.")
        await update_files(session, config_data, github_pat)

    # Schedule periodic updates
    hass.data[DOMAIN][entry.entry_id]["update_job"] = async_track_time_interval(
        hass, periodic_update, UPDATE_INTERVAL
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

    # Close the aiohttp session
    session = aiohttp.ClientSession()
    await session.close()

    # Remove entry data
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle cleanup when the SMARTi integration is uninstalled."""
    _LOGGER.info("Cleaning up files and directories for SMARTi integration.")

    for path, files in FILES_TO_DELETE.items():
        # Delete specific files in the directory
        for file_name in files:
            file_path = os.path.join(path, file_name)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    _LOGGER.info(f"Deleted file: {file_path}")
                except Exception as e:
                    _LOGGER.error(f"Failed to delete file {file_path}: {e}")

        # Delete the directory if it's empty
        if os.path.exists(path):
            try:
                if not os.listdir(path):  # Check if the directory is empty
                    shutil.rmtree(path)
                    _LOGGER.info(f"Deleted empty directory: {path}")
                else:
                    _LOGGER.info(f"Directory {path} is not empty, skipping deletion.")
            except Exception as e:
                _LOGGER.error(f"Failed to delete directory {path}: {e}")

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
