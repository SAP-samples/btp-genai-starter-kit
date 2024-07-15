import logging
from library.load import load
from library.process import (
    Image,
    TabularDataImageProcessor,
    VisualReasoningProcessor,
)
from library.ai import AiCore
from utils.env import init_env
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


def main():
    # Load environment variables
    init_env()

    print("\n")
    print("Welcome to the AI Core Image Processing Examples")
    print("================================================")

    def print_header():
        print("Please select an example to run:\n")
        print("1: Visual Reasoning on Image")
        print("2: Read Tabular Data in Image")
        print("3: Exit (or press Ctrl+C)")
        print("\n")

    while True:
            print_header()
            option = input("Which example would you like to run? ").strip()

            if option == "1":
                execute_visual_reasoning_example()
                continue
            elif option == "2":
                execute_tabular_data_example()
                continue
            elif option == "3":
                break
            else:
                print("Invalid input. Please enter a number between 1 and ")


if __name__ == "__main__":
    main()
