import logging
import os

from pydantic import BaseModel
import requests

log = logging.getLogger(__name__)


class Media(BaseModel):
    src: str
    data: str = ""
    media_type: str
    output_schema: dict


class MediaProcessor:
    def __init__(self, media: Media):
        self.src = media.src
        self.data = media.data
        self.media_type = media.media_type
        self.schema = media.output_schema

    def trigger_inference_via_http(self, auth_token) -> str:
        """
        Sends an HTTP request to the AI Core API for inference.

        Args:
            auth_token (str): The authentication token for the API.
            image (str): The base64-encoded image to be processed.

        Returns:
            str: The response from the API as a JSON string.
        """

        api_base = os.environ.get("AICORE_BASE_URL")
        deployment_id = os.environ.get("AICORE_DEPLOYMENT")
        resource_group = os.environ.get("AICORE_RESOURCE_GROUP") or "default"

        api_url = f"{api_base}/v2/inference/deployments/{deployment_id}/invoke"
        # Create the headers for the request
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "AI-Resource-Group": resource_group,
        }

        prompt = f"""
            Act as an AI Assistant that reads all information from a given media.
            The output should comply with the following JSON schema: {self.schema}.
            The value should be NULL if you are not sure.
            Think step by step.
            The result should ONLY contain the JSON object as output WITHOUT any additional explanations.
        """

        data = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": self.media_type,
                                "data": self.data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }

        response = requests.post(url=api_url, headers=headers, json=data, timeout=20)

        response_as_json = response.json()

        return response_as_json["content"][0]["text"]
