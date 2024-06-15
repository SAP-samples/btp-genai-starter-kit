import logging
import base64
import os
import requests

log = logging.getLogger(__name__)


def fetch_and_encode(url: str) -> str:
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


def load_images_from_dir(image_path: str) -> dict:
    """
    Load images from a directory and return a dictionary containing the image filenames as keys
    and their base64-encoded contents as values.

    Args:
        image_path (str): The path to the directory containing the images.

    Returns:
        dict: A dictionary containing the image filenames as keys and their base64-encoded contents as values.
    """
    files = os.listdir(image_path)

    image_files = [
        file
        for file in files
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".gif"))
    ]

    image_dict = {}

    for file in image_files:
        file_path = os.path.join(image_path, file)
        with open(file_path, "rb") as f:
            image = f.read()
        image_base64 = base64.b64encode(image).decode("utf-8")
        image_dict[file] = image_base64

    return image_dict
