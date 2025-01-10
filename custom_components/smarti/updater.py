import os
import logging
import aiofiles
import aiohttp
import shutil
import asyncio
import stat
from urllib.parse import urlparse

_LOGGER = logging.getLogger(__name__)

DOMAIN = "smarti"

# Repository URLs for Basic and Pro versions
GITHUB_REPO_URL_PRO = "https://api.github.com/repos/Prosono/SMARTi_Configuration/contents/"
GITHUB_REPO_URL_BASIC = "https://api.github.com/repos/Prosono/SMARTi_Configuration_Basic/contents/"

# Function to get the correct GitHub repository URL based on the version
def get_github_repo_url(version):
    return GITHUB_REPO_URL_PRO if version == "pro" else GITHUB_REPO_URL_BASIC

# Common local paths where files will be saved
PACKAGES_PATH = "/config/packages/smartipackages/"
THEMES_PATH = "/config/themes/smarti_themes/"
DASHBOARDS_PATH = "/config/smartidashboards/"
IMAGES_PATH = "/config/www/images/smarti_images"
CUSTOM_CARDS_PATH = "/config/www/smarticards/"
ANIMATIONS_PATH = "/config/www/smartianimations/"
LICENSE_PATH = "/config/www/smartilicense/"

# Files to delete before re-downloading
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
    "smarti_powerflow_gridfee_automations",
]

DASHBOARDS_FILES_TO_DELETE = [
    "smarti-custom-cards-test.yaml",
]

ANIMATION_FILES_TO_DELETE = []
THEME_FILES_TO_DELETE = []
IMAGE_FILES_TO_DELETE = []
CUSTOM_CARDS_FILES_TO_DELETE = []
SMARTI_LICENSES_TO_DELETE = []

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

async def download_file(url: str, dest: str, session: aiohttp.ClientSession, github_pat: str, force_update: bool = False):
    """Download a single file from GitHub to a local destination, optionally forcing update."""
    headers = {"Authorization": f"Bearer {github_pat}"}
    try:
        if os.path.exists(dest) and not force_update:
            _LOGGER.info(f"File {dest} already exists. Skipping download.")
            return

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
    """Return a list of download URLs for 'file' items at a specific GitHub folder level (non-recursive)."""
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
    """Create a directory if it doesn't exist."""
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            _LOGGER.info(f"Created directory {path}")
        else:
            _LOGGER.info(f"Directory {path} already exists")
    except Exception as e:
        _LOGGER.error(f"Error creating directory {path}: {str(e)}")

async def clear_specific_files(directory: str, files_to_delete: list):
    """Delete specific files in a directory asynchronously."""
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

async def update_files(session: aiohttp.ClientSession, config_data: dict, github_pat: str):
    """Update files by fetching from GitHub and saving locally."""
    version = config_data.get("version", "basic")  # 'basic' or 'pro'
    mode = config_data.get("mode", "automatic")    # 'automatic' or 'manual'

    GITHUB_REPO_URL = get_github_repo_url(version)

    PACKAGES_URL = GITHUB_REPO_URL + "packages/smartipackages/"
    DASHBOARDS_URL = GITHUB_REPO_URL + "dashboards/smartidashboards/"
    THEMES_URL = GITHUB_REPO_URL + "themes/smarti_themes/"
    IMAGES_URL = GITHUB_REPO_URL + "www/images/smarti_images/"
    CUSTOM_CARDS_URL = GITHUB_REPO_URL + "www/smarticards/"
    ANIMATIONS_URL = GITHUB_REPO_URL + "www/smartianimations/"
    LICENSE_URL = GITHUB_REPO_URL + "www/smartilicense/"

    if not await validate_api_token(github_pat, session):
        _LOGGER.error("Invalid GitHub PAT. Aborting update process.")
        return

    # Clear specific files before downloading
    await clear_specific_files(PACKAGES_PATH, PACKAGES_FILES_TO_DELETE)
    await clear_specific_files(DASHBOARDS_PATH, DASHBOARDS_FILES_TO_DELETE)
    await clear_specific_files(THEMES_PATH, THEME_FILES_TO_DELETE)
    await clear_specific_files(IMAGES_PATH, IMAGE_FILES_TO_DELETE)
    if mode == "automatic":
        await clear_specific_files(CUSTOM_CARDS_PATH, CUSTOM_CARDS_FILES_TO_DELETE)
    await clear_specific_files(ANIMATIONS_PATH, ANIMATION_FILES_TO_DELETE)
    await clear_specific_files(LICENSE_PATH, SMARTI_LICENSES_TO_DELETE)

    # Ensure directories exist
    paths_to_ensure = [
        PACKAGES_PATH,
        DASHBOARDS_PATH,
        THEMES_PATH,
        IMAGES_PATH,
        ANIMATIONS_PATH,
        LICENSE_PATH,
    ]

    if mode == "automatic":
        paths_to_ensure.append(CUSTOM_CARDS_PATH)

    for path in paths_to_ensure:
        ensure_directory(path)

    # Download package files
    package_files = await get_files_from_github(PACKAGES_URL, session, github_pat)
    for file_url in package_files:
        file_name = os.path.basename(urlparse(file_url).path)
        if mode == "manual" and file_name == "smarti_custom_cards_package.yaml":
            _LOGGER.info(f"Skipping file {file_name} in manual mode.")
            continue
        dest_path = os.path.join(PACKAGES_PATH, file_name)
        await download_file(file_url, dest_path, session, github_pat)

    # Download dashboard files
    dashboard_files = await get_files_from_github(DASHBOARDS_URL, session, github_pat)
    for file_url in dashboard_files:
        file_name = os.path.basename(urlparse(file_url).path)
        dest_path = os.path.join(DASHBOARDS_PATH, file_name)
        await download_file(file_url, dest_path, session, github_pat, force_update=True)

    # Download theme files
    themes_files = await get_files_from_github(THEMES_URL, session, github_pat)
    for file_url in themes_files:
        file_name = os.path.basename(urlparse(file_url).path)
        dest_path = os.path.join(THEMES_PATH, file_name)
        await download_file(file_url, dest_path, session, github_pat)

    # Download image files
    image_files = await get_files_from_github(IMAGES_URL, session, github_pat)
    for file_url in image_files:
        file_name = os.path.basename(urlparse(file_url).path)
        dest_path = os.path.join(IMAGES_PATH, file_name)
        await download_file(file_url, dest_path, session, github_pat)

    # Download animations files
    animation_files = await get_files_from_github(ANIMATIONS_URL, session, github_pat)
    for file_url in animation_files:
        file_name = os.path.basename(urlparse(file_url).path)
        dest_path = os.path.join(ANIMATIONS_PATH, file_name)
        await download_file(file_url, dest_path, session, github_pat)

    # Download license files
    license_files = await get_files_from_github(LICENSE_URL, session, github_pat)
    for file_url in license_files:
        file_name = os.path.basename(urlparse(file_url).path)
        dest_path = os.path.join(LICENSE_PATH, file_name)
        await download_file(file_url, dest_path, session, github_pat)

    _LOGGER.info("All updates completed successfully.")
