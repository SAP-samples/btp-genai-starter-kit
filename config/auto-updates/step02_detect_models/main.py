from library.util.io import write_file
from library.util.logging import initLogger
from library.constants.folders import FILE_ENV, FILE_TERRAFORM_VARIABLE_AVAILABLE_MODELS
from library.constants.terraform import TEMPLATE_AI_CORE_MODEL
from library.fetch.aicore import AiCoreMetadata
from pathlib import Path
import logging
from dotenv import load_dotenv
import sys

log = logging.getLogger(__name__)
initLogger()


# Main function
def main(arguments: list[str]):
    load_dotenv(dotenv_path=str(FILE_ENV), verbose=True)

    log.header("Preparing the environment for using the AI Core service.")

    # Extract the metadata for the AI Core system
    ai_core_metadata = AiCoreMetadata()
    available_models = ai_core_metadata.availableModels
    write_models_into_terraform_file(available_models)


def write_models_into_terraform_file(models: list[str]):
    model_text = ""
    for model in models:
        # add a new line only, if it is not the last model
        if model != models[-1]:
            model_text += f'        "{model}",\n'
        else:
            model_text += f'        "{model}",'

    file_content = TEMPLATE_AI_CORE_MODEL.replace("<<AVAILABLE_MODELS>>", model_text)
    write_file(Path(FILE_TERRAFORM_VARIABLE_AVAILABLE_MODELS), file_content)


if __name__ == "__main__":
    main(sys.argv)
