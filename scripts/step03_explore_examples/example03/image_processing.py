import logging
import json
from modules.load import fetch_and_encode
from modules.process import Media, MediaProcessor
from modules.ai import AiCore

log = logging.getLogger(__name__)


def get_image_sample():
    return Media(
        src="https://upload.wikimedia.org/wikipedia/commons/c/c1/FourMetricInstruments.JPG",
        media_type="image/jpeg",
        output_schema={
            "type": "array",
            "items": {
                "properties": {
                    "deviceName": {
                        "type": "string",
                        "description": "The name of the measurement device",
                    },
                    "value": {
                        "type": "number",
                        "description": "The value of the measurement",
                    },
                    "unitOfMeasurement": {
                        "type": "string",
                        "description": "The unit of measurement",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence level of the output in percent",
                    },
                }
            },
        },
    )


def main():
    sample = get_image_sample()

    sample.data = fetch_and_encode(sample.src)

    # image_path = "example03/data/images"
    # load_from_fs(images_path)

    media_processor = MediaProcessor(sample)

    auth_token = AiCore().get_token()
    output = media_processor.trigger_inference_via_http(auth_token=auth_token)

    print("Output: %s", output)


if __name__ == "__main__":
    main()
