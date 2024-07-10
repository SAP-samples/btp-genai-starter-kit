import logging
import sys
import os
from typing import List
from pydantic import BaseModel
import requests

log = logging.getLogger(__name__)


class Image(BaseModel):
    src: str
    mime_type: str
    data: str


class ImageProcessorBase:
    def is_valid_image(self, image: Image):
        if not image:
            raise ValueError("Image must be set")
        if not image.src:
            raise ValueError("Image source must be set")
        if not image.mime_type:
            raise ValueError("Image mime type must be set")
        if not image.data:
            raise ValueError("Image data must be set")

    def get_prompt(self) -> str:
        raise NotImplementedError("Method get_prompt must be implemented")

    def execute(self, messages: List[dict], auth_token: str) -> str:
        try:
            """
            Executes the image processing by sending a POST request to the AI Core API.

            Args:
                messages (List[dict]): A list of message dictionaries.
                auth_token (str): The authentication token for accessing the API.

            Returns:
                str: The processed image content as text.

            Raises:
                requests.exceptions.RequestException: If there is an error in the request.
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

            data = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "messages": messages,
            }

            log.info("Executing image processing...")

            response = requests.post(url=api_url, headers=headers, json=data, timeout=20)

            response_as_json = response.json()

            log.info("Image processed")

            return response_as_json["content"][0]["text"]
        except requests.exceptions.RequestException as e:
            log.error("Error processing image: {e}")
            sys.exit()


class TabularDataImageProcessor(ImageProcessorBase):
    def __init__(self, image):
        super().is_valid_image(image)
        self.image = image

    def get_prompt(self) -> str:
        return """
            Search for information listed as a table or as list.
            Remove any unnecessary information for example trailing characters.
            Read the name, the values and unit of measurement of the values.
            The output should be a table using markdown as format.
            Come up with meaningful column names if the names are not provided on the image.
            Scan the image line by line and think step by step.
            The output should contain ONLY the markdown table WITHOUT any additional explanations.
        """

    def execute(self, auth_token: str) -> str:
        prompt = self.get_prompt()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": self.image.mime_type,
                            "data": self.image.data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        return super().execute(messages, auth_token)


class VisualReasoningProcessor(ImageProcessorBase):
    def __init__(self, image):
        super().is_valid_image(image)
        self.image = image

    def get_prompt(self) -> str:
        return """
            Act as supervisor who is responsible to detect potential risks based on the information provided in an image.
            In case if any risks hav been detected give me a detailed explanation of the risks and the potential impact.
            The output should be a bullet list using markdown format containing the following list items:
            - Risk Detected (Yes, No)
            - Potential Impact
            - Mitigation Strategy
            - Risk Level (Low, Medium, High)
            Reason step by step about the potential outcome.
            If no risks have been detected, return a message that no risks have been found.
            Provite the result WITHOUT any additional explanations.
        """

    def execute(self, auth_token: str) -> str:
        prompt = self.get_prompt()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": self.image.mime_type,
                            "data": self.image.data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        return super().execute(messages, auth_token)
