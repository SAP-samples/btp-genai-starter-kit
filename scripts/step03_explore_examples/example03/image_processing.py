import logging
from modules.load import load
from modules.process import (
    Image,
    ImageProcessor,
    FewShotProcessor,
    get_read_random_data_in_image_prompt,
    get_read_tabular_data_in_image_prompt,
    get_visual_reasoning_prompt,
)
from modules.ai import AiCore
import os

log = logging.getLogger(__name__)


def create_src_path(src):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, src)


def execute_object_detection_sample():
    src = (
        "https://upload.wikimedia.org/wikipedia/commons/c/c1/FourMetricInstruments.JPG"
    )

    image_data: str = load(src)

    image = Image(
        src=src,
        mime_type="image/jpeg",
        data=image_data,
    )

    # Get auth token
    auth_token = AiCore().get_token()

    # Get prompt and execute image processing
    prompt = get_read_random_data_in_image_prompt(
        schema={
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
    )

    image_processor = ImageProcessor(image=image)
    output = image_processor.execute(prompt=prompt, auth_token=auth_token)
    print(output)


def execute_visual_reasoning_sample():
    src = create_src_path("images/oil-on-street.jpeg")

    image_data: str = load(src)

    image = Image(
        src=src,
        mime_type="image/jpeg",
        data=image_data,
    )
    # Get auth token
    auth_token = AiCore().get_token()

    # Get prompt and execute image processing
    prompt = get_visual_reasoning_prompt()
    image_processor = ImageProcessor(image=image)
    output = image_processor.execute(prompt=prompt, auth_token=auth_token)
    print(output)


def execute_read_tabular_data_in_image_sample():
    src = create_src_path("images/supplement-ingredients.png")

    image_data: str = load(src)

    image = Image(
        src=src,
        mime_type="image/png",
        data=image_data,
    )
    # Get auth token
    auth_token = AiCore().get_token()

    # Get prompt and execute image processing
    prompt = get_read_tabular_data_in_image_prompt()
    image_processor = ImageProcessor(image=image)
    output = image_processor.execute(prompt=prompt, auth_token=auth_token)
    print(output)


def execute_few_shot_sample():
    def create(src):
        image_data: str = load(create_src_path(src))
        return Image(
            src=src,
            mime_type="image/png",
            data=image_data,
        )

    example1 = create("images/egg-basket-with-defects-example-1.png")
    example2 = create("images/egg-basket-with-defects-example-2.png")
    example3 = create("images/egg-basket-with-defects-example-3.png")
    image = create("images/egg-basket-with-defects.png")

    # Get auth token
    auth_token = AiCore().get_token()

    image_processor = FewShotProcessor()

    output = image_processor.execute(
        image,
        example1,
        example2,
        example3,
        auth_token=auth_token,
    )

    print(output)


def main():
    print("Please select an example to run:")
    print("1: Object Detection")
    print("2: Visual Reasoning")
    print("3: Read Tabular Data in Image")
    print("4: Few Shot Promping with object detection")
    print("5 or Press Ctrl+C: Exit\n")

    while True:
        try:
            example = input("Which example would you like to run?").strip()
            if example == "1":
                execute_object_detection_sample()
                continue
            elif example == "2":
                execute_visual_reasoning_sample()
                continue
            elif example == "3":
                execute_read_tabular_data_in_image_sample()
                continue
            elif example == "4":
                execute_few_shot_sample()
                continue
            elif example == "5":
                break
            else:
                print("Invalid input. Please enter a number between 1 and 5")
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 5")


if __name__ == "__main__":
    main()
