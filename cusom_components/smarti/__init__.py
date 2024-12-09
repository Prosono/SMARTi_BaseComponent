import logging
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the SMARTi integration."""
    _LOGGER.info("Setting up the SMARTi integration.")
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up SMARTi from a config entry."""
    _LOGGER.info("Setting up SMARTi from config entry.")

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {}

    # Forward the setup to the update platform
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "update")
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    _LOGGER.info("Unloading SMARTi config entry.")

    await hass.config_entries.async_forward_entry_unload(entry, "update")

    hass.data[DOMAIN].pop(entry.entry_id)
    return True

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle migration of config entry if needed."""
    _LOGGER.info(f"Migrating SMARTi entry from version {entry.version}")

    # Define the current version of your integration
    current_version = 1

    if entry.version == current_version:
        _LOGGER.info("No migration necessary")
        return True

    # Implement migration logic if needed
    # For now, we'll assume no changes are needed and simply update the version
    hass.config_entries.async_update_entry(entry, version=current_version)
    _LOGGER.info(f"Migration to version {current_version} successful")
    return True
