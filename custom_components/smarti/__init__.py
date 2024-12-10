import logging
import aiohttp
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.event import async_track_time_interval
from .const import DOMAIN
from .updater import update_files

_LOGGER = logging.getLogger(__name__)

# Interval for periodic updates (e.g., every hour)
UPDATE_INTERVAL = timedelta(hours=1)

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
    github_pat = entry.data.get("api_token")
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
