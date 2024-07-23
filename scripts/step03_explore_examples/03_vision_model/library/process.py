import logging
import sys
from typing import List
from pydantic import BaseModel
from langchain_core.language_models.llms import BaseLLM
from langchain_core.messages import HumanMessage

log = logging.getLogger(__name__)


class Image(BaseModel):
    src: str
    mime_type: str
    data: str


class ImageProcessorBase:
    def __init__(self, image, llm_with_vision: BaseLLM):
        self.is_valid_image(image)
        self.image = image
        self.llm_with_vision = llm_with_vision

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

    def execute_via_sdk(self, messages: List[dict]) -> str:
        try:
            response = self.llm_with_vision.invoke(messages)
            return response.content
        except Exception as e:
            log.error(f"Error executing via SDK: {str(e)}")
            sys.exit()


class TabularDataImageProcessor(ImageProcessorBase):

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

    def execute(self) -> str:
        prompt = self.get_prompt()
        return super().execute_via_sdk(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.image.data}"
                            },
                        },
                    ]
                )
            ]
        )


class VisualReasoningProcessor(ImageProcessorBase):

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

    def execute(self) -> str:
        prompt = self.get_prompt()
        return super().execute_via_sdk(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{self.image.data}"
                            },
                        },
                    ]
                )
            ]
        )
