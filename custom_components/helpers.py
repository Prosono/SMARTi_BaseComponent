import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)
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