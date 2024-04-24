from library.util.io import write_file
from library.util.logging import initLogger
from library.constants.folders import FILE_METADATA_AI_CORE_KEY, FILE_ENV
from library.model.aicore import AiCoreMetadataJsonEncoder
from library.fetch.aicore import AiCoreMetadata
from pathlib import Path
import logging
import json
from dotenv import load_dotenv
import sys

log = logging.getLogger(__name__)
initLogger()


# Main function
def main(arguments: list[str]):
    # Check if the user wants to see the HTTP debug information
    show_http_debug = False
    if len(arguments) == 2:
        if arguments[1] == "http_debug":
            show_http_debug = True

    load_dotenv(dotenv_path=str(FILE_ENV), verbose=True)

    log.header("Preparing the environment for using the AI Core service.")

    # Extract the metadata for the AI Core system
    ai_core_metadata = AiCoreMetadata(show_http_debug)
    write_file(
        Path(FILE_METADATA_AI_CORE_KEY),
        json.dumps(ai_core_metadata, indent=2, cls=AiCoreMetadataJsonEncoder),
    )


if __name__ == "__main__":
    main(sys.argv)
