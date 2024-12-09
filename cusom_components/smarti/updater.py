import os
import logging
import base64
import aiofiles
import aiohttp
import json
import time  # Import for cache-busting
import stat  # Import for file permissions
import shutil
import asyncio

_LOGGER = logging.getLogger(__name__)

DOMAIN = "smarti"

GITHUB_REPO_URL = "https://api.github.com/repos/Prosono/smarti/contents/"
PACKAGES_URL = GITHUB_REPO_URL + "packages/"
DASHBOARDS_URL = GITHUB_REPO_URL + "dashboards/"
SMARTIUPDATER_URL = GITHUB_REPO_URL + "custom_components/smartiupdater/"
THEMES_URL = GITHUB_REPO_URL + "themes/smarti_themes/"
IMAGES_URL = GITHUB_REPO_URL + "www/images/smarti_images/"
CUSTOM_CARD_RADAR_URL = GITHUB_REPO_URL + "www/community/weather-radar-card/"

VERSION_URL = GITHUB_REPO_URL + "version.json"

PACKAGES_PATH = "/config/packages/"
THEMES_PATH = "/config/themes/smarti_themes/"
DASHBOARDS_PATH = "/config/dashboards/"
SMARTIUPDATER_PATH = "/config/custom_components/smartiupdater/"
IMAGES_PATH = "/config/www/images/smarti_images"
CUSTOM_CARD_RADAR_PATH = "/config/www/community/weather-radar-card/"

PACKAGES_FILES_TO_DELETE = [
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
    "smarti_powerflow_gridfee_automations"
]

DASHBOARDS_FILES_TO_DELETE = {
    "SMARTi_Language_Norsk.yaml",
    "SMARTi_Language_English.yaml"
}

_LOGGER = logging.getLogger(__name__)

def log_file_size(filepath: str, description: str):
    """Log the size of a file with a description."""
    try:
        file_size = os.path.getsize(filepath)
        _LOGGER.info(f"{description} - File size of {filepath}: {file_size} bytes")
    except Exception as e:
        _LOGGER.error(f"Failed to get file size for {filepath}: {str(e)}")

def ensure_writable(filepath: str):
    """Ensure that the file has writable permissions."""
    try:
        # Set the file permissions to be writable by the user (owner)
        os.chmod(filepath, stat.S_IWUSR | stat.S_IRUSR)
        _LOGGER.info(f"Permissions set to writable for {filepath}.")
    except Exception as e:
        _LOGGER.error(f"Failed to set writable permissions for {filepath}: {str(e)}")

def ensure_directory_exists(directory_path: str):
    """Ensure that a directory exists."""
    if not os.path.exists(directory_path):
        _LOGGER.error(f"The directory {directory_path} does not exist.")
        raise FileNotFoundError(f"The directory {directory_path} does not exist.")
    else:
        _LOGGER.info(f"Directory {directory_path} exists.")

async def download_file(url: str, dest: str, session: aiohttp.ClientSession):
    try:
        _LOGGER.info(f"Attempting to download file from {url} to {dest}")

        # Ensure 'dest' is the full path to a file, not a directory
        if os.path.isdir(dest):
            dest = os.path.join(dest, 'flows.json')  # Ensure saving to file, not directory

        async with session.get(url) as response:
            response.raise_for_status()
            content = await response.read()

            async with aiofiles.open(dest, "wb") as file:
                await file.write(content)

        _LOGGER.info(f"File successfully downloaded and saved to {dest}")
    except aiohttp.ClientError as http_err:
        _LOGGER.error(f"HTTP error occurred while downloading {url}: {http_err}")
    except Exception as e:
        _LOGGER.error(f"Error occurred while downloading {url}: {str(e)}")

async def get_files_from_github(url: str, session: aiohttp.ClientSession):
    try:
        _LOGGER.info(f"Fetching file list from {url}")
        async with session.get(url) as response:
            response.raise_for_status()
            files = await response.json()

            _LOGGER.debug(f"API response from {url}: {files}")

            # Check if 'files' is a list (directory) or a dictionary (single file)
            if isinstance(files, list):
                file_urls = [file['download_url'] for file in files if file.get('type') == 'file']
                _LOGGER.info(f"Found {len(file_urls)} files at {url}")
            elif isinstance(files, dict):
                # Handle case where a single file dict is returned
                if 'download_url' in files:
                    file_urls = [files['download_url']]
                    _LOGGER.info(f"Found a single file at {url}")
                else:
                    _LOGGER.error(f"No download URL found for the file at {url}")
                    return []
            else:
                _LOGGER.error(f"Unexpected format from {url}")
                return []

            return file_urls
    except aiohttp.ClientError as http_err:
        _LOGGER.error(f"HTTP error occurred while fetching file list from {url}: {http_err}")
        return []
    except Exception as e:
        _LOGGER.error(f"Error occurred while fetching file list from {url}: {str(e)}")
        return []

def ensure_directory(path: str):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            _LOGGER.info(f"Created directory {path}")
        else:
            _LOGGER.info(f"Directory {path} already exists")
    except Exception as e:
        _LOGGER.error(f"Error creating directory {path}: {str(e)}")


async def clear_specific_files(directory: str, files_to_delete: list):
    """Delete only specific files in the given directory."""
    for filename in files_to_delete:
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            await asyncio.to_thread(os.remove, file_path)
            _LOGGER.info(f"Deleted file: {file_path}")
        else:
            _LOGGER.info(f"File {file_path} does not exist or is not a file.")


async def clear_directory(directory_path: str):
    """Delete all files in the specified directory asynchronously."""
    try:
        if os.path.exists(directory_path):
            # Use asyncio.to_thread to run the blocking shutil.rmtree call in a separate thread
            await asyncio.to_thread(shutil.rmtree, directory_path)
            await asyncio.to_thread(os.makedirs, directory_path)  # Recreate the directory asynchronously
            _LOGGER.info(f"Cleared and recreated directory: {directory_path}")
        else:
            await asyncio.to_thread(os.makedirs, directory_path)  # Create the directory if it doesn't exist
            _LOGGER.info(f"Directory {directory_path} did not exist, so it was created.")
    except Exception as e:
        _LOGGER.error(f"Failed to clear directory {directory_path}: {str(e)}")

async def update_files(session: aiohttp.ClientSession, config_data: dict):
    # Clear the packages and dashboards directories before downloading new files
    #await clear_directory(PACKAGES_PATH)   # Await the coroutine
    await clear_specific_files(PACKAGES_PATH, PACKAGES_FILES_TO_DELETE)
    await clear_specific_files(DASHBOARDS_PATH, DASHBOARDS_FILES_TO_DELETE)
    #await clear_directory(DASHBOARDS_PATH) # Await the coroutine

    ensure_directory(PACKAGES_PATH)
    ensure_directory(DASHBOARDS_PATH)
    ensure_directory(SMARTIUPDATER_PATH)
    ensure_directory(THEMES_PATH)
    ensure_directory(IMAGES_PATH)
    #ensure_directory(NODE_RED_PATH)
    ensure_directory(CUSTOM_CARD_RADAR_PATH)

    # Get and download package files
    package_files = await get_files_from_github(PACKAGES_URL, session)
    for file_url in package_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(PACKAGES_PATH, file_name)
            _LOGGER.info(f"Saving package file to {dest_path}")
            await download_file(file_url, dest_path, session)

    # Get and download dashboard files
    if config_data.get("update_dashboards"):
        dashboard_files = await get_files_from_github(DASHBOARDS_URL, session)
        for file_url in dashboard_files:
            if file_url:
                file_name = os.path.basename(file_url)
                dest_path = os.path.join(DASHBOARDS_PATH, file_name)
                _LOGGER.info(f"Saving dashboard file to {dest_path}")
                await download_file(file_url, dest_path, session)

    # Get and download custom component files
    smartiupdater_files = await get_files_from_github(SMARTIUPDATER_URL, session)
    for file_url in smartiupdater_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(SMARTIUPDATER_PATH, file_name)
            _LOGGER.info(f"Saving SmartiUpdater file to {dest_path}")
            await download_file(file_url, dest_path, session)

    # Get and download Themes files
    themes_files = await get_files_from_github(THEMES_URL, session)
    for file_url in themes_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(THEMES_PATH, file_name)
            _LOGGER.info(f"Saving themes file to {dest_path}")
            await download_file(file_url, dest_path, session)

    # Get and download IMAGE files
    image_files = await get_files_from_github(IMAGES_URL, session)
    for file_url in image_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(IMAGES_PATH, file_name)
            _LOGGER.info(f"Saving image file to {dest_path}")
            await download_file(file_url, dest_path, session)

    # Get and download CUSTOM CARDS files
    radar_card_files = await get_files_from_github(CUSTOM_CARD_RADAR_URL, session)
    for file_url in radar_card_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(CUSTOM_CARD_RADAR_PATH, file_name)
            _LOGGER.info(f"Saving card files to {dest_path}")
            await download_file(file_url, dest_path, session)



async def get_latest_version(session: aiohttp.ClientSession):
    try:
        cache_buster = f"?nocache={str(time.time())}"
        async with session.get(VERSION_URL + cache_buster) as response:
            response.raise_for_status()
            version_info = await response.json()
            _LOGGER.debug(f"Fetched version info: {version_info}")

            # Decode the base64 content
            encoded_content = version_info.get("content", "")
            if encoded_content:
                decoded_content = base64.b64decode(encoded_content).decode("utf-8")
                version_data = json.loads(decoded_content)
                latest_version = version_data.get("version", "unknown")
                return latest_version
            else:
                _LOGGER.error("No content found in the version info.")
                return "unknown"
    except aiohttp.ClientError as http_err:
        _LOGGER.error(f"HTTP error occurred while fetching version info: {http_err}")
        return "unknown"
    except Exception as e:
        _LOGGER.error(f"Error occurred while fetching version info: {str(e)}")
        return "unknown"

async def check_for_update(session: aiohttp.ClientSession, current_version: str):
    try:
        latest_version = await get_latest_version(session)
        _LOGGER.debug(f"Current version: {current_version}, Latest version: {latest_version}")
        return current_version != latest_version, latest_version
    except aiohttp.ClientError as http_err:
        _LOGGER.error(f"HTTP error occurred while checking for update: {http_err}")
        return False, "unknown"
    except Exception as e:
        _LOGGER.error(f"Error occurred while checking for update: {str(e)}")
        return False, "unknown"

async def update_manifest_version(latest_version: str):
    manifest_file = "/config/custom_components/smartiupdater/manifest.json"
    try:
        async with aiofiles.open(manifest_file, 'r+') as file:
            manifest_data = json.loads(await file.read())
            manifest_data['version'] = latest_version
            await file.seek(0)
            await file.write(json.dumps(manifest_data, indent=4))
            await file.truncate()
        _LOGGER.info(f"Updated manifest file version to {latest_version}")
    except Exception as e:
        _LOGGER.error(f"Error updating manifest file: {str(e)}")

