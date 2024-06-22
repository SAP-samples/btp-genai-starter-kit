import logging
from modules.load import load
from modules.process import (
    Image,
    RandomMeasurementDeviceImageProcessor,
    TabularDataImageProcessor,
    VisualReasoningProcessor,
    FewShotProcessor,
)
from modules.ai import AiCore
import os

log = logging.getLogger(__name__)


def create_src_path(src):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, src)


def load_image(src: str, mime_type: str) -> Image:
    """
    Factory to load an image from the specified source path and return an Image object.

    Args:
        src (str): The source path of the image.
        mime_type (str): The MIME type of the image.

    Returns:
        Image: An Image object containing the loaded image data.

    """
    is_url = src.startswith("http://") or src.startswith("https://")
    full_path = create_src_path(src)
    image_data: str = load(src) if is_url else load(full_path)
    return Image(
        src=src,
        mime_type=mime_type,
        data=image_data,
    )


def execute_measurement_device_example():
    auth_token = AiCore().get_token()

    image = load_image(
        "https://upload.wikimedia.org/wikipedia/commons/c/c1/FourMetricInstruments.JPG",
        "image/jpeg",
    )

    schema = {
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
            }
        },
    }

    image_processor = RandomMeasurementDeviceImageProcessor(
        image=image, output_schema=schema
    )

    result = image_processor.execute(auth_token=auth_token)

    print(result)


def execute_visual_reasoning_example():
    image = load_image("images/oil-on-street.jpeg", "image/jpeg")
    auth_token = AiCore().get_token()
    image_processor = VisualReasoningProcessor(image=image)
    output = image_processor.execute(auth_token=auth_token)
    print(output)


def execute_tabular_data_example():
    image = load_image("images/supplement-ingredients.png", "image/png")
    auth_token = AiCore().get_token()
    image_processor = TabularDataImageProcessor(image=image)
    output = image_processor.execute(auth_token=auth_token)
    print(output)


def execute_few_shot_example():
    example1 = load_image("images/egg-basket-with-defects-example-1.png", "image/png")
    example2 = load_image("images/egg-basket-with-defects-example-2.png", "image/png")
    example3 = load_image("images/egg-basket-with-defects-example-3.png", "image/png")
    image = load_image("images/egg-basket-with-defects.png", "image/png")

    # Get auth token
    auth_token = AiCore().get_token()

    image_processor = FewShotProcessor(image, example1, example2, example3)
    output = image_processor.execute(auth_token=auth_token)
    print(output)


def main():
    print("Please select an example to run:")
    print("1: Measure Device Detection")
    print("2: Visual Reasoning")
    print("3: Read Tabular Data in Image")
    print("4: Few Shot Promping with object detection")
    print("5 or Press Ctrl+C: Exit\n")

    while True:
        try:
            example = input("Which example would you like to run?").strip()
            if example == "1":
                execute_measurement_device_example()
                continue
            elif example == "2":
                execute_visual_reasoning_example()
                continue
            elif example == "3":
                execute_tabular_data_example()
                continue
            elif example == "4":
                execute_few_shot_example()
                continue
            elif example == "5":
                break
            else:
                print("Invalid input. Please enter a number between 1 and 5")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5")


if __name__ == "__main__":
    main()
