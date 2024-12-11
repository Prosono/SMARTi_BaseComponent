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

GITHUB_REPO_URL = "https://api.github.com/repos/Prosono/SMARTi_Configuration/contents/"

PACKAGES_URL = GITHUB_REPO_URL + "packages/"
DASHBOARDS_URL = GITHUB_REPO_URL + "dashboards/"
THEMES_URL = GITHUB_REPO_URL + "themes/smarti_themes/"
IMAGES_URL = GITHUB_REPO_URL + "www/images/smarti_images/"
#CUSTOM_CARD_RADAR_URL = GITHUB_REPO_URL + "www/community/weather-radar-card/"

PACKAGES_PATH = "/config/packages/"
THEMES_PATH = "/config/themes/smarti_themes/"
DASHBOARDS_PATH = "/config/dashboards/"
IMAGES_PATH = "/config/www/images/smarti_images"
#CUSTOM_CARD_RADAR_PATH = "/config/www/community/weather-radar-card/"

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

async def validate_api_token(api_token: str, session: aiohttp.ClientSession):
    headers = {"Authorization": f"Bearer {api_token}"}
    try:
        async with session.get("https://api.github.com/user", headers=headers) as response:
            if response.status == 200:
                _LOGGER.info("API token is valid.")
                return True
            else:
                _LOGGER.error(f"Invalid API token: {response.status}")
                return False
    except Exception as e:
        _LOGGER.error(f"Error validating API token: {str(e)}")
        return False     

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

async def download_file(url: str, dest: str, session: aiohttp.ClientSession, github_pat: str):
    headers = {"Authorization": f"Bearer {github_pat}"}
    try:
        # Parse the URL to remove query parameters
        parsed_url = urlparse(url)
        clean_url = parsed_url._replace(query=None).geturl()

        _LOGGER.info(f"Attempting to download file from {clean_url} to {dest}")

        async with session.get(clean_url, headers=headers) as response:
            response.raise_for_status()
            content = await response.read()

            async with aiofiles.open(dest, "wb") as file:
                await file.write(content)

        _LOGGER.info(f"File successfully downloaded and saved to {dest}")
    except aiohttp.ClientError as http_err:
        _LOGGER.error(f"HTTP error occurred while downloading {url}: {http_err}")
    except Exception as e:
        _LOGGER.error(f"Error occurred while downloading {url}: {str(e)}")

async def get_files_from_github(url: str, session: aiohttp.ClientSession, github_pat: str):
    headers = {"Authorization": f"Bearer {github_pat}"}
    try:
        async with session.get(url, headers=headers) as response:
            response.raise_for_status()
            files = await response.json()
            if isinstance(files, list):
                return [file["download_url"] for file in files if file.get("type") == "file"]
    except aiohttp.ClientError as http_err:
        _LOGGER.error(f"HTTP error occurred while fetching file list from {url}: {http_err}")
        raise
    except Exception as e:
        _LOGGER.error(f"Unexpected error occurred while fetching file list: {str(e)}")
        raise
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
    if not os.path.exists(directory):
        _LOGGER.warning(f"Directory {directory} does not exist, skipping file deletion.")
        return
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

async def update_files(session: aiohttp.ClientSession, config_data: dict, github_pat: str):
    """Update files by fetching from GitHub and saving locally."""
    if not await validate_api_token(github_pat, session):
        _LOGGER.error("Invalid GitHub PAT. Aborting update process.")
        return

    await clear_specific_files(PACKAGES_PATH, PACKAGES_FILES_TO_DELETE)
    await clear_specific_files(DASHBOARDS_PATH, PACKAGES_FILES_TO_DELETE)

    ensure_directory(PACKAGES_PATH)
    ensure_directory(DASHBOARDS_PATH)
    ensure_directory(THEMES_PATH)
    ensure_directory(IMAGES_PATH)
    #ensure_directory(CUSTOM_CARD_RADAR_PATH)


    package_files = await get_files_from_github(PACKAGES_URL, session, github_pat)
    for file_url in package_files:
        if file_url:
            # Extract the file name without query parameters
            file_name = os.path.basename(urlparse(file_url).path)
            dest_path = os.path.join(PACKAGES_PATH, file_name)
            _LOGGER.info(f"Saving package file to {dest_path}")
            await download_file(file_url, dest_path, session, github_pat)

    # Get and download dashboard files
    if config_data.get("update_dashboards"):
        dashboard_files = await get_files_from_github(DASHBOARDS_URL, session, github_pat)
        for file_url in dashboard_files:
            if file_url:
                file_name = os.path.basename(file_url)
                dest_path = os.path.join(DASHBOARDS_PATH, file_name)
                _LOGGER.info(f"Saving dashboard file to {dest_path}")
                await download_file(file_url, dest_path, session, github_pat)

    # Get and download Themes files
    themes_files = await get_files_from_github(THEMES_URL, session, github_pat)
    for file_url in themes_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(THEMES_PATH, file_name)
            _LOGGER.info(f"Saving themes file to {dest_path}")
            await download_file(file_url, dest_path, session, github_pat)

    # Get and download IMAGE files
    image_files = await get_files_from_github(IMAGES_URL, session, github_pat)
    for file_url in image_files:
        if file_url:
            file_name = os.path.basename(file_url)
            dest_path = os.path.join(IMAGES_PATH, file_name)
            _LOGGER.info(f"Saving image file to {dest_path}")
            await download_file(file_url, dest_path, session, github_pat)

    # Get and download CUSTOM CARDS files
    #radar_card_files = await get_files_from_github(CUSTOM_CARD_RADAR_URL, session, github_pat)
    #for file_url in radar_card_files:
    #    if file_url:
    #        file_name = os.path.basename(file_url)
    #        dest_path = os.path.join(CUSTOM_CARD_RADAR_PATH, file_name)
    #        _LOGGER.info(f"Saving card files to {dest_path}")
    #        await download_file(file_url, dest_path, session, github_pat)



