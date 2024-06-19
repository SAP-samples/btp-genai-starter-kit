import logging
import os
from typing import List
from pydantic import BaseModel
import requests

log = logging.getLogger(__name__)


def get_read_tabular_data_in_image_prompt() -> str:
    return """
        Act as an AI Assistant that reads information from an given image.
        Search for information listed as a table or as list.
        Remove any unnecessary information for example trailing characters.
        Read the name, the values and unit of measurement of the values.
        The output should be a table using markdown as format.
        Come up with meaningful column names if the names are not provided on the image.
        Scan the image line by line and think step by step.
        The output should contain ONLY the markdown table WITHOUT any additional explanations.
    """


def get_few_show_prompt() -> str:
    return """
        Search for information listed as a table or as list.
        Remove any unnecessary information for example trailing characters.
        Read the name, the values and unit of measurement of the values.
        The output should be a table using markdown as format.
        Come up with meaningful column names if the names are not provided on the image.
        Scan the image line by line and think step by step.
        The output should contain ONLY the markdown table WITHOUT any additional explanations.
    """


def get_visual_reasoning_prompt() -> str:
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


def get_read_random_data_in_image_prompt(schema: dict) -> str:
    if not schema:
        raise ValueError("Schema must be set")

    return f"""
        Act as an physicist whos task is to read values from given measurement instuments in an image.
        Identify the device, read all the measures and choose the respective unit of measurement.
        Estimate the measure if needed.
        The output should comply with the following JSON schema: {schema}.
        Think step by step.
        The result should ONLY contain the JSON object as output WITHOUT any additional explanations.
    """


class Image(BaseModel):
    src: str
    mime_type: str
    data: str


class FewShotProcessor:
    def execute(
        self,
        image: Image,
        example1: Image,
        example2: Image,
        example3: Image,
        auth_token: str,
    ) -> str:
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

        data = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 12000,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "How many broken eggs are on the image?",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": example1.mime_type,
                                "data": example1.data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Answer: { total: 12, broken: 1 }",
                        },
                        {
                            "type": "text",
                            "text": "How many broken eggs are on the image?",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": example2.mime_type,
                                "data": example2.data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Answer: { total: 12, broken: 8 }",
                        },
                        {
                            "type": "text",
                            "text": "How many broken eggs are on the image?",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": example3.mime_type,
                                "data": example3.data,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Answer: { total: 41, broken: 13 }",
                        },
                        {
                            "type": "text",
                            "text": "How many eggs are on the image? Think step by step. Reply with: { total: ?, broken: ? }",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image.mime_type,
                                "data": image.data,
                            },
                        },
                    ],
                },
            ],
        }

        log.info("Executing image processing...")
        response = requests.post(url=api_url, headers=headers, json=data, timeout=20)
        response_as_json = response.json()
        log.info("Image processed")

        return response_as_json["content"][0]["text"]


class ImageProcessor:
    def __init__(self, image: Image):
        if not image.src or not image.mime_type or not image.data:
            raise ValueError("Image attributes must be set")
        self.image = image

    def execute(self, prompt: str, auth_token: str) -> str:
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
                                "media_type": self.image.mime_type,
                                "data": self.image.data,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        }

        response = requests.post(url=api_url, headers=headers, json=data, timeout=20)

        response_as_json = response.json()

        log.info("Image from %s was successfully processed", self.image.src)

        return response_as_json["content"][0]["text"]
