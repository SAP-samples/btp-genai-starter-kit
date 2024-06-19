import logging
import base64
import os
import requests

log = logging.getLogger(__name__)


def load(src: str) -> str:
    """
    Helper function to load data from a given source.

    Args:
        src (str): The data source, which can be either a URL or a file path.

    Returns:
        str: The loaded data as a string.
    """
    if src.startswith("http://") or src.startswith("https://"):
        return fetch_from_url(src)
    else:
        return load_from_fs(src)


def fetch_from_url(url: str) -> str:
    """
    Fetches content from the given URL and returns it as a base64 encoded string.

    Args:
        url (str): The URL of the content to fetch.

    Returns:
        str: The base64 encoded string representation of the fetched data.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(url, headers=headers, timeout=10)
    content = response.content

    content_base64 = base64.b64encode(content).decode("utf-8")
    return content_base64


def load_from_fs(image_path: str) -> dict:
    """
    Load an image file from the specified directory and return it as a base64-encoded string.

    Args:
        image_path (str): The path to the image file.

    Returns:
        dict: A dictionary containing the base64-encoded image string.

    Raises:
        ValueError: If the image file format is not supported.

    """
    if not image_path.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
        raise ValueError(
            "Invalid image file format. Supported formats are .png, .jpg, .jpeg, .gif, and .webp"
        )

    try:
        with open(image_path, "rb") as f:
            image = f.read()
        return base64.b64encode(image).decode("utf-8")
    except Exception as e:
        log.error("Error loading image from directory: %s", e)
        raise
