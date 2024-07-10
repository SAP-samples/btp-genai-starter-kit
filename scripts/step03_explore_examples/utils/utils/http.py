import requests
import io


def fetch_file(url):
    """
    Fetches the content of a file from the given URL.

    Args:
        url (str): The URL of the file to fetch.

    Returns:
        bytes: The content of the file as bytes.

    Raises:
        requests.exceptions.RequestException: If an error occurs while making the request.

    """
    response = requests.get(url, timeout=20)
    return response.content
