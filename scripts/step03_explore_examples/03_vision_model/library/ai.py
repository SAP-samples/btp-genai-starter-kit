from dataclasses import dataclass
import os
import logging
import base64
import requests

log = logging.getLogger(__name__)


@dataclass
class AiCore:
    def __init__(self):
        self.auth_url = os.environ.get("AICORE_AUTH_URL")
        self.client_id = os.environ.get("AICORE_CLIENT_ID")
        self.client_secret = os.environ.get("AICORE_CLIENT_SECRET")

    def get_token(self) -> str:
        """
        Retrieves an access token using client credentials.

        Returns:
            str: The access token.

        Raises:
            requests.exceptions.HTTPError: If the request to retrieve the access token fails.
        """
        client_id = self.client_id
        client_secret = self.client_secret
        auth_url = self.auth_url

        auth_string = f"{client_id}:{client_secret}"
        byte_data = auth_string.encode("utf-8")
        client_secret_b64_decoded = base64.b64encode(byte_data).decode("utf-8")

        auth_endpoint = f"{auth_url}/oauth/token?grant_type=client_credentials"
        headers = {"Authorization": f"Basic {client_secret_b64_decoded}"}

        response = requests.post(url=auth_endpoint, headers=headers, timeout=10)

        if response.status_code != 200:
            raise requests.exceptions.HTTPError(
                f"Failed to retrieve access token. Status code: {response.status_code}"
            )

        access_token = response.json()["access_token"]

        return access_token
